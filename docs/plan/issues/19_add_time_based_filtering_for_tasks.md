# GitHub Issue #19: Add time-based filtering for tasks (today, this week, overdue)

**Issue:** [#19](https://github.com/denhamparry/todoist-mcp/issues/19)
**Status:** Open
**Date:** 2025-11-28
**Priority:** Medium-High

## Problem Statement

Currently, `todoist_get_tasks` returns all tasks regardless of their due date, making it difficult to focus on what needs to be done today or this week. Users asking questions like "Show me the tasks I need to get done by today" receive all tasks rather than filtered results.

### Current Behavior

- `todoist_get_tasks` only supports `project_id` and `label` filtering (server.py:156-234)
- No time-based filtering capability
- Returns all tasks when users ask about today's tasks, weekly tasks, or overdue items
- Users must manually parse all results to find relevant time-based tasks

### Expected Behavior

- Support time-based queries using Todoist's native filter syntax
- Enable queries like "tasks due today", "overdue tasks", "this week's tasks"
- Allow combining time filters with existing project/label filters
- Support Todoist's full filter query language for flexibility

## Current State Analysis

### Relevant Code/Config

**Current Implementation:** `src/todoist_mcp/server.py:156-234`

```python
@mcp.tool()
async def todoist_get_tasks(
    project_id: Optional[str] = None,
    label: Optional[str] = None,
) -> str:
    """Get tasks from Todoist with optional filtering.

    Args:
        project_id: Filter tasks by project ID
        label: Filter tasks by label name

    Returns:
        Formatted list of tasks with IDs, content, due dates, and priorities
    """
    # ...validation...
    task_generator = await todoist.get_tasks(project_id=project_id, label=label)
    # ...formatting...
```

**Missing:** `filter` parameter support

### Todoist API Support

The Todoist REST API v2 GET /tasks endpoint supports:

- `project_id` (String) - Filter by project ID ✅ Currently supported
- `section_id` (String) - Filter by section ID ❌ Not supported
- `label` (String) - Filter by label name ✅ Currently supported
- **`filter` (String) - Filter by any supported filter query** ❌ **Not supported (target of this issue)**
- `lang` (String) - Language for filter syntax
- `ids` (Array) - List of specific task IDs

**Parameter precedence:**

1. `filter` (with or without `lang`) - highest priority
2. `ids`
3. `label`, `project_id`, or `section_id` - lowest priority

When `filter` is provided, it takes precedence over other parameters.

### Related Context

**Test Structure:** `tests/test_server.py`

- Lines 137-163: `test_todoist_get_tasks_success` - Uses monkeypatch with `create_async_gen_mock`
- Lines 166-180: `test_todoist_get_tasks_empty` - Tests empty results
- Lines 184-206: `test_todoist_get_tasks_with_label` - Tests label filtering
- Lines 592-612: Validation tests for empty parameters

**Test Pattern:**

```python
monkeypatch.setattr(
    todoist_mcp.server.todoist, "get_tasks", create_async_gen_mock([task_obj])
)
```

**Validation Pattern:** Uses helper functions in server.py:43-130

- `validate_project_id()` - Lines 80-91
- `validate_non_empty_string()` - Lines 117-129

**Documentation:** `README.md` - Lines 196-202 reference tool documentation section

## Solution Design

### Approach

**Add `filter` parameter to `todoist_get_tasks`** that accepts Todoist's native filter query syntax.

**Rationale:**

- ✅ Flexible - Supports any Todoist filter query (time, priority, labels, etc.)
- ✅ Native - Uses Todoist's documented filter language
- ✅ Consistent - Aligns with Todoist's REST API v2
- ✅ Extensible - No need for future updates when Todoist adds filter features
- ✅ Simple - Single parameter addition with validation

**Alternative Approach Considered:**

Predefined enum options (`due_filter: "today" | "overdue" | "week"`)

- ❌ Limited - Only supports pre-defined filters
- ❌ Inflexible - Can't combine filters or use advanced queries
- ❌ Maintenance burden - Need to update when users want new filters

### Implementation

#### 1. Add `filter` parameter to function signature

**File:** `src/todoist_mcp/server.py:156-159`

```python
@mcp.tool()
async def todoist_get_tasks(
    project_id: Optional[str] = None,
    label: Optional[str] = None,
    filter: Optional[str] = None,  # NEW PARAMETER
) -> str:
```

#### 2. Update docstring

**File:** `src/todoist_mcp/server.py:160-168`

```python
"""Get tasks from Todoist with optional filtering.

Args:
    project_id: Filter tasks by project ID
    label: Filter tasks by label name
    filter: Todoist filter query (e.g., "today", "overdue", "7 days")
            See: <https://todoist.com/help/articles/introduction-to-filters>
            Note: filter takes precedence over project_id and label parameters

Returns:
    Formatted list of tasks with IDs, content, due dates, and priorities
"""
```

#### 3. Add validation for filter parameter

**File:** `src/todoist_mcp/server.py:174-181` (after existing validations)

```python
# Validation
if error := validate_project_id(project_id):
    logger.warning(f"Validation failed in todoist_get_tasks: {error}")
    return error
if label is not None and (not label or not label.strip()):
    error_msg = "Error: Label filter cannot be empty"
    logger.warning(f"Validation failed in todoist_get_tasks: {error_msg}")
    return error_msg
# NEW VALIDATION
if filter is not None and (not filter or not filter.strip()):
    error_msg = "Error: Filter cannot be empty"
    logger.warning(f"Validation failed in todoist_get_tasks: {error_msg}")
    return error_msg
```

#### 4. Update logging

**File:** `src/todoist_mcp/server.py:169-172`

```python
logger.info(
    f"Tool called: todoist_get_tasks - "
    f"project_id={project_id!r} label={label!r} filter={filter!r}"
)
```

#### 5. Pass filter parameter to API

**File:** `src/todoist_mcp/server.py:187`

```python
task_generator = await todoist.get_tasks(
    project_id=project_id,
    label=label,
    filter=filter  # NEW PARAMETER
)
```

### Benefits

1. **User-friendly:** Natural language queries work seamlessly
   - "Show me tasks due today" → `filter="today"`
   - "What's overdue?" → `filter="overdue"`
   - "Tasks this week" → `filter="7 days"`

2. **Powerful:** Support for complex queries
   - `filter="today & p1"` - High priority tasks today
   - `filter="(today | overdue) & @work"` - Work tasks today or overdue
   - `filter="7 days & !#Personal"` - Week tasks excluding Personal project

3. **Consistent:** Uses Todoist's official filter syntax
   - Users familiar with Todoist app can use same queries
   - Links to Todoist documentation for reference

4. **Compatible:** Works alongside existing filters
   - Note: API precedence means `filter` will override `project_id`/`label` if both provided
   - Documentation clarifies this behavior

## Implementation Plan

### Step 1: Add filter validation helper function

**File:** `src/todoist_mcp/server.py:115-130` (after `validate_labels`)

**Changes:**

```python
def validate_filter(filter_query: Optional[str]) -> Optional[str]:
    """Validate filter parameter (non-empty string if provided).

    Args:
        filter_query: Todoist filter query to validate

    Returns:
        Error message if invalid, None if valid
    """
    if filter_query is not None and (not filter_query or not filter_query.strip()):
        return "Error: Filter query cannot be empty"
    return None
```

**Testing:**

```bash
pytest tests/test_server.py::test_validate_filter -v
```

### Step 2: Update todoist_get_tasks function

**File:** `src/todoist_mcp/server.py:156-234`

**Changes:**

1. Add `filter` parameter to signature (line 158)
2. Update docstring with filter documentation (lines 160-168)
3. Update logging to include filter parameter (lines 169-172)
4. Add filter validation using new helper function (after line 181)
5. Pass filter parameter to `todoist.get_tasks()` API call (line 187)

**Code Example:**

```python
@mcp.tool()
async def todoist_get_tasks(
    project_id: Optional[str] = None,
    label: Optional[str] = None,
    filter: Optional[str] = None,
) -> str:
    """Get tasks from Todoist with optional filtering.

    Args:
        project_id: Filter tasks by project ID
        label: Filter tasks by label name
        filter: Todoist filter query (e.g., "today", "overdue", "7 days")
                See: https://todoist.com/help/articles/introduction-to-filters
                Note: When provided, filter takes precedence over project_id/label

    Returns:
        Formatted list of tasks with IDs, content, due dates, and priorities
    """
    logger.info(
        f"Tool called: todoist_get_tasks - "
        f"project_id={project_id!r} label={label!r} filter={filter!r}"
    )

    # Validation
    if error := validate_project_id(project_id):
        logger.warning(f"Validation failed in todoist_get_tasks: {error}")
        return error
    if error := validate_filter(filter):
        logger.warning(f"Validation failed in todoist_get_tasks: {error}")
        return error
    if label is not None and (not label or not label.strip()):
        error_msg = "Error: Label filter cannot be empty"
        logger.warning(f"Validation failed in todoist_get_tasks: {error_msg}")
        return error_msg

    try:
        logger.debug("Fetching tasks from Todoist API")
        tasks = []
        task_generator = await todoist.get_tasks(
            project_id=project_id,
            label=label,
            filter=filter
        )
        async for task_batch in task_generator:
            tasks.extend(task_batch)

        # ... rest of function unchanged ...
```

**Testing:**

```bash
pytest tests/test_server.py::test_todoist_get_tasks_success -v
```

### Step 3: Add unit tests for filter parameter

**File:** `tests/test_server.py` (after line 206)

**Add Test Cases:**

1. **Test filter parameter validation (empty filter)**

```python
@pytest.mark.asyncio
async def test_get_tasks_empty_filter(mock_api_token):
    """Test todoist_get_tasks rejects empty filter"""
    from todoist_mcp.server import todoist_get_tasks

    result = await todoist_get_tasks(filter="")
    assert result == "Error: Filter query cannot be empty"

    result = await todoist_get_tasks(filter="   ")
    assert result == "Error: Filter query cannot be empty"
```

2. **Test filter parameter with "today" query**

```python
@pytest.mark.asyncio
async def test_todoist_get_tasks_with_filter_today(mock_api_token, monkeypatch, mock_task):
    """Test todoist_get_tasks with filter='today'"""
    from todoist_api_python.models import Task
    from tests.conftest import create_async_gen_mock
    import todoist_mcp.server

    # Create Task object from mock data
    task_obj = Task.from_dict(mock_task)

    # Mock to verify filter parameter is passed
    monkeypatch.setattr(
        todoist_mcp.server.todoist, "get_tasks", create_async_gen_mock([task_obj])
    )

    from todoist_mcp.server import todoist_get_tasks

    result = await todoist_get_tasks(filter="today")

    # Verify response format
    assert "Found 1 task(s):" in result
    assert "[12345] Test task" in result
```

3. **Test filter parameter with "overdue" query**

```python
@pytest.mark.asyncio
async def test_todoist_get_tasks_with_filter_overdue(mock_api_token, monkeypatch, mock_task):
    """Test todoist_get_tasks with filter='overdue'"""
    from todoist_api_python.models import Task
    from tests.conftest import create_async_gen_mock
    import todoist_mcp.server

    task_obj = Task.from_dict(mock_task)

    monkeypatch.setattr(
        todoist_mcp.server.todoist, "get_tasks", create_async_gen_mock([task_obj])
    )

    from todoist_mcp.server import todoist_get_tasks

    result = await todoist_get_tasks(filter="overdue")
    assert "Found 1 task(s):" in result
```

4. **Test filter parameter with complex query**

```python
@pytest.mark.asyncio
async def test_todoist_get_tasks_with_filter_complex(mock_api_token, monkeypatch, mock_task):
    """Test todoist_get_tasks with complex filter query"""
    from todoist_api_python.models import Task
    from tests.conftest import create_async_gen_mock
    import todoist_mcp.server

    task_obj = Task.from_dict(mock_task)

    monkeypatch.setattr(
        todoist_mcp.server.todoist, "get_tasks", create_async_gen_mock([task_obj])
    )

    from todoist_mcp.server import todoist_get_tasks

    # Test combining time and priority filters
    result = await todoist_get_tasks(filter="today & p1")
    assert "Found 1 task(s):" in result
```

5. **Test logging includes filter parameter**

```python
@pytest.mark.asyncio
async def test_get_tasks_logs_filter(mock_api_token, caplog, monkeypatch):
    """Test that filter parameter is logged"""
    from tests.conftest import create_async_gen_mock
    import todoist_mcp.server

    monkeypatch.setattr(
        todoist_mcp.server.todoist, "get_tasks", create_async_gen_mock([])
    )

    from todoist_mcp.server import todoist_get_tasks

    with caplog.at_level(logging.INFO):
        await todoist_get_tasks(filter="today")

    # Verify filter parameter is logged
    assert any("filter='today'" in record.message for record in caplog.records)
```

**Testing:**

```bash
pytest tests/test_server.py -k "filter" -v
pytest tests/test_server.py --cov=src/todoist_mcp --cov-report=term-missing
```

### Step 4: Update README.md documentation

**File:** `README.md` (find tool documentation section, likely around line 100-200)

**Add to todoist_get_tasks documentation:**

```markdown
#### todoist_get_tasks

Get tasks with optional filtering by project, label, or time-based filters.

**Parameters:**
- `project_id` (optional): Filter tasks by project ID
- `label` (optional): Filter tasks by label name
- `filter` (optional): Todoist filter query for advanced filtering

**Filter Examples:**

Time-based filters:
- `filter="today"` - Tasks due today
- `filter="overdue"` - Overdue tasks
- `filter="7 days"` - Tasks due in the next 7 days
- `filter="no date"` - Tasks without a due date

Priority filters:
- `filter="p1"` - Priority 1 (urgent) tasks
- `filter="p2"` - Priority 2 (high) tasks

Combined filters:
- `filter="today & p1"` - Urgent tasks due today
- `filter="(today | overdue) & @work"` - Work tasks that are today or overdue
- `filter="7 days & !#Personal"` - Week's tasks excluding Personal project

**Note:** When using `filter`, it takes precedence over `project_id` and `label` parameters due to Todoist API behavior.

**Filter Syntax Reference:** [Todoist Filter Guide](https://todoist.com/help/articles/introduction-to-filters)

**Example Usage:**

```python
# Get today's tasks
result = await todoist_get_tasks(filter="today")

# Get overdue high-priority tasks
result = await todoist_get_tasks(filter="overdue & p1")

# Get work tasks for the week
result = await todoist_get_tasks(filter="7 days & @work")
```

**Testing:**

Manually verify README renders correctly on GitHub.

### Step 5: Run integration tests

**Testing:**

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src/todoist_mcp --cov-report=html --cov-report=term-missing

# Run integration tests (if real API token available)
pytest tests/test_integration.py -v
```

**Manual integration test (optional):**

```bash
# Set environment variables
export TODOIST_API_TOKEN="your_real_token"
export LOG_LEVEL=DEBUG

# Run server and test with Claude Code
uv run python -m todoist_mcp.server

# In Claude, ask:
# - "Show me tasks due today"
# - "What tasks are overdue?"
# - "Show me high priority tasks this week"
```

### Step 6: Run pre-commit hooks

**Command:**

```bash
pre-commit run --all-files
```

**Expected checks:**

- Trailing whitespace removal
- End-of-file fixing
- YAML/JSON validation
- Secret detection (gitleaks)
- Markdown linting

**Fix any issues:**

```bash
# If pre-commit makes changes, review and commit them
git add -A
git status
```

## Testing Strategy

### Unit Testing

**Test Coverage Goals:** >90% coverage for new code

**Test Cases:**

1. **Validation tests:**
   - ✅ Empty filter string rejected
   - ✅ Whitespace-only filter rejected
   - ✅ Valid filter strings accepted
   - ✅ None filter value accepted (optional parameter)

2. **Parameter passing tests:**
   - ✅ Filter parameter passed to API correctly
   - ✅ Filter works with other parameters
   - ✅ Filter takes precedence (API behavior)

3. **Logging tests:**
   - ✅ Filter parameter logged in INFO messages
   - ✅ Filter validation failures logged as WARNING

4. **Response formatting tests:**
   - ✅ Tasks returned with filter applied
   - ✅ Empty results handled correctly
   - ✅ Error messages formatted properly

### Integration Testing

**Note:** Integration tests require real Todoist API token

**Test Case 1: Filter by "today"**

Setup:

1. Create tasks with various due dates in Todoist
2. Ensure at least one task is due today

Test:

```bash
# Expected: Returns only tasks due today
todoist_get_tasks(filter="today")
```

Expected Result:

- Only tasks with due date = today returned
- Tasks with other due dates not included
- Response includes task details (ID, content, due date)

**Test Case 2: Filter by "overdue"**

Setup:

1. Create tasks with past due dates

Test:

```bash
# Expected: Returns only overdue tasks
todoist_get_tasks(filter="overdue")
```

Expected Result:

- Only tasks with due date < today returned
- Current and future tasks not included

**Test Case 3: Filter by "7 days"**

Setup:

1. Create tasks due within next week
2. Create tasks due beyond next week

Test:

```bash
# Expected: Returns tasks due in next 7 days
todoist_get_tasks(filter="7 days")
```

Expected Result:

- Tasks due in next 7 days returned
- Tasks beyond 7 days not included
- Today's tasks included

**Test Case 4: Combined filter "today & p1"**

Setup:

1. Create high priority task due today
2. Create low priority task due today
3. Create high priority task due tomorrow

Test:

```bash
# Expected: Returns only high-priority tasks due today
todoist_get_tasks(filter="today & p1")
```

Expected Result:

- Only tasks matching both conditions returned
- Filters work in combination

**Test Case 5: Invalid filter syntax**

Test:

```bash
# Expected: API error handled gracefully
todoist_get_tasks(filter="invalid_syntax_@@@")
```

Expected Result:

- Error message returned to user
- No server crash
- Error logged appropriately

### Regression Testing

**Existing functionality to verify:**

1. **Get all tasks (no filters):** `todoist_get_tasks()`
   - Verify still returns all tasks when no filter provided

2. **Filter by project:** `todoist_get_tasks(project_id="123")`
   - Verify existing project filtering still works

3. **Filter by label:** `todoist_get_tasks(label="work")`
   - Verify existing label filtering still works

4. **Empty parameter validation:** All existing validation tests
   - Verify empty project_id still rejected
   - Verify empty label still rejected

5. **Rate limit handling:** Existing rate limit tests
   - Verify rate limit errors still handled correctly

6. **Logging:** Existing logging tests
   - Verify logs still capture all parameters

## Success Criteria

Implementation is complete when all criteria are met:

- [x] `filter` parameter added to `todoist_get_tasks` function signature
- [x] Validation helper function `validate_filter()` implemented
- [x] Filter parameter validation implemented with proper error messages
- [x] Filter parameter passed to Todoist API `get_tasks()` call
- [x] Logging updated to include filter parameter in INFO logs
- [x] Function docstring updated with filter examples and reference link
- [x] Unit tests added for filter validation (empty filter rejection)
- [x] Unit tests added for filter queries ("today", "overdue", "7 days", complex)
- [x] Unit tests verify filter parameter is logged correctly
- [x] All unit tests pass with >90% coverage
- [x] README.md updated with filter documentation and examples
- [x] README.md includes link to Todoist filter syntax reference
- [x] Pre-commit hooks pass (trailing whitespace, end-of-file, linting)
- [x] No regression in existing tests (all existing tests still pass)
- [x] Integration test with real API confirms filter queries work (optional)

## Files Modified

1. **`src/todoist_mcp/server.py`** - Core implementation
   - Add `validate_filter()` helper function (after line 115)
   - Update `todoist_get_tasks()` signature (line 158)
   - Update docstring with filter documentation (lines 160-168)
   - Update logging to include filter parameter (lines 169-172)
   - Add filter validation call (after line 181)
   - Pass filter to API call (line 187)
   - Estimated changes: ~30 lines added/modified

2. **`tests/test_server.py`** - Unit tests
   - Add `test_get_tasks_empty_filter()` - Validation test
   - Add `test_todoist_get_tasks_with_filter_today()` - Today filter test
   - Add `test_todoist_get_tasks_with_filter_overdue()` - Overdue filter test
   - Add `test_todoist_get_tasks_with_filter_complex()` - Complex query test
   - Add `test_get_tasks_logs_filter()` - Logging test
   - Estimated changes: ~80 lines added

3. **`README.md`** - Documentation
   - Update `todoist_get_tasks` tool documentation section
   - Add filter parameter description
   - Add filter examples (time-based, priority, combined)
   - Add note about parameter precedence
   - Add link to Todoist filter syntax reference
   - Estimated changes: ~40 lines added

## Related Issues and Tasks

### Depends On

- None - This is a standalone feature

### Blocks

- None identified

### Related

- Issue #1: Create Todoist MCP Server (completed - base implementation)
- Issue #4: Add proper unit tests (completed - test patterns established)
- Issue #7: Add logging infrastructure (completed - logging pattern to follow)
- Issue #8: Rate limit handling (completed - error handling pattern to follow)

### Enables

Future enhancements that become easier with filter support:

- Custom saved filter queries
- Filter presets for common queries
- Time-based task notifications
- Smart task suggestions based on filters

## References

- **GitHub Issue:** [#19 - Add time-based filtering for tasks](https://github.com/denhamparry/todoist-mcp/issues/19)
- **Todoist REST API v2:** [Get Active Tasks](https://developer.todoist.com/rest/v2/#get-active-tasks)
- **Todoist Filter Guide:** [Introduction to Filters](https://todoist.com/help/articles/introduction-to-filters)
- **Current Implementation:** src/todoist_mcp/server.py:156-234
- **Test Patterns:** tests/test_server.py:137-206
- **Documentation:** README.md (tool documentation section)

## Notes

### Key Insights

1. **API Precedence:** The Todoist API applies parameters in precedence order:
   - `filter` (highest) > `ids` > `label`/`project_id`/`section_id` (lowest)
   - When `filter` is provided, it overrides `project_id` and `label`
   - Must document this behavior clearly for users

2. **Validation Pattern:** Project follows consistent validation pattern:
   - Dedicated validation helper functions (e.g., `validate_project_id`)
   - Return `Optional[str]` error messages
   - Log warnings for validation failures
   - Return error message to user (don't raise exceptions)

3. **Test Pattern:** Existing tests use `monkeypatch` with `create_async_gen_mock`:
   - Mock the `todoist.get_tasks()` async generator
   - Use `Task.from_dict()` to create test objects
   - Assert partial string matches for flexible validation
   - Separate tests for success, empty, validation, and error cases

4. **Logging Standard:** Consistent logging pattern across all tools:
   - INFO level: Tool calls with all parameters
   - DEBUG level: API calls
   - WARNING level: Validation failures
   - ERROR level: API errors with stack traces

### Alternative Approaches Considered

1. **Predefined Enum Filter Options** ❌

   ```python
   due_filter: Literal["today", "overdue", "week", "no_date"]
   ```

   - Rejected: Too limited, can't support Todoist's full filter syntax
   - Would require code changes for every new filter type users want

2. **Separate Parameter for Each Filter Type** ❌

   ```python
   due_date: Optional[str] = None,  # "today", "tomorrow", etc.
   priority: Optional[int] = None,   # 1-4
   time_range: Optional[int] = None, # days
   ```

   - Rejected: Complex API, difficult to combine filters
   - Doesn't match Todoist's native query language

3. **Chosen: Native Filter String** ✅

   ```python
   filter: Optional[str] = None,  # Todoist filter query
   ```

   - Flexible - Supports all Todoist filter capabilities
   - Simple - Single parameter
   - Native - Uses Todoist's documented syntax
   - Extensible - No code changes needed for new filters
   - Consistent - Matches Todoist API design

### Implementation Best Practices

1. **Follow Existing Patterns:**
   - Use same validation pattern as other parameters
   - Use same logging format as other tools
   - Use same test structure as existing tests
   - Use same error handling as other API calls

2. **Minimal Changes:**
   - Only add what's necessary for filter support
   - Don't refactor existing working code
   - Keep changes focused and reviewable

3. **Comprehensive Testing:**
   - Test validation (empty, whitespace, valid)
   - Test API parameter passing
   - Test logging includes new parameter
   - Test with real-world filter queries
   - Ensure no regression in existing tests

4. **Clear Documentation:**
   - Document parameter precedence behavior
   - Provide practical filter examples
   - Link to Todoist's official filter documentation
   - Include examples in docstring and README

### Monitoring Approach

After deployment, monitor for:

1. **Filter Usage Patterns:**
   - Log analysis: Which filters are most commonly used?
   - Helps prioritize future filter-related features

2. **Filter Syntax Errors:**
   - Track API errors related to invalid filter syntax
   - May indicate need for client-side validation or better docs

3. **Performance:**
   - Compare response times with/without filters
   - Todoist API may have different performance characteristics for filtered queries

4. **User Questions:**
   - Monitor user questions about filter syntax
   - May indicate documentation gaps or UX issues
