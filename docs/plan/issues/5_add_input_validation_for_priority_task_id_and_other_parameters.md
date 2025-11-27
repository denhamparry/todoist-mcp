# GitHub Issue #5: Add input validation for priority, task_id, and other parameters

**Issue:** [#5](https://github.com/denhamparry/todoist-mcp/issues/5)
**Status:** Open
**Labels:** enhancement
**Priority:** HIGH
**Date:** 2025-11-27

## Problem Statement

MCP tools currently lack input validation, which could lead to unclear error messages or unexpected behavior when invalid data is provided. Users may pass invalid parameters (e.g., priority out of range, empty task IDs, malformed data) and receive confusing API errors instead of clear, user-friendly validation messages.

### Current Behavior

The current implementation in `src/todoist_mcp/server.py` accepts parameters without validation:

**Example - Priority parameter (no validation):**

```python
async def todoist_create_task(
    content: str,
    description: Optional[str] = None,
    project_id: Optional[str] = None,
    due_string: Optional[str] = None,
    priority: Optional[int] = None,  # No validation - any int accepted
    labels: Optional[List[str]] = None,
) -> str:
```

**Example - Task ID parameter (no validation):**

```python
async def todoist_update_task(
    task_id: str,  # No validation - empty strings accepted
    content: Optional[str] = None,
    ...
) -> str:
```

**Current error messages** (from API):

- Invalid priority: Generic API error (unclear to user)
- Empty task_id: API error or confusing failure
- Invalid project_id: API error without context
- Malformed labels: May fail silently or with API error

**User experience issues:**

1. Unclear error messages don't explain what's wrong
2. Errors happen after API call (wasted network round-trip)
3. No guidance on valid parameter ranges/formats
4. Hard to debug which parameter is invalid

### Expected Behavior

Tools should validate input parameters **before** making API calls and return clear, user-friendly error messages that:

1. **Explain what's wrong** - Specific parameter and issue
2. **Show valid ranges** - Tell user what values are acceptable
3. **Fail fast** - Validate before API call
4. **Guide correction** - Help user fix the input

**Example validation messages:**

```python
# Priority validation
"Error: Priority must be between 1 and 4 (received: 5)"

# Task ID validation
"Error: Task ID is required and cannot be empty"

# Project ID validation
"Error: Project ID cannot be empty"

# Labels validation
"Error: Labels must be a list of strings (received: 'urgent')"
```

## Current State Analysis

### Server Implementation

**File:** `src/todoist_mcp/server.py`

**7 MCP tools requiring validation:**

1. **`todoist_get_tasks`** (lines 28-72)
   - `project_id: Optional[str]` - Should validate non-empty if provided
   - `label: Optional[str]` - Should validate non-empty if provided

2. **`todoist_create_task`** (lines 75-108)
   - `content: str` - Should validate non-empty (required)
   - `priority: Optional[int]` - Should validate 1-4 range if provided
   - `labels: Optional[List[str]]` - Should validate list of strings if provided
   - `project_id: Optional[str]` - Should validate non-empty if provided

3. **`todoist_update_task`** (lines 111-147)
   - `task_id: str` - Should validate non-empty (required)
   - `priority: Optional[int]` - Should validate 1-4 range if provided
   - `labels: Optional[List[str]]` - Should validate list of strings if provided
   - Note: At least one update field should be provided

4. **`todoist_complete_task`** (lines 150-167)
   - `task_id: str` - Should validate non-empty (required)

5. **`todoist_delete_task`** (lines 170-187)
   - `task_id: str` - Should validate non-empty (required)

6. **`todoist_get_projects`** (lines 190-215)
   - No parameters requiring validation

7. **`todoist_get_labels`** (lines 218-241)
   - No parameters requiring validation

### Validation Requirements Summary

**Priority Parameter:**

- Must be integer between 1 and 4 (inclusive)
- Todoist API mapping: 1=normal, 2=medium, 3=high, 4=urgent
- Used in: `todoist_create_task`, `todoist_update_task`

**Task ID Parameter:**

- Must be non-empty string
- Required parameter (not optional)
- Used in: `todoist_update_task`, `todoist_complete_task`, `todoist_delete_task`

**Project ID Parameter:**

- Must be non-empty string if provided
- Optional parameter
- Used in: `todoist_get_tasks`, `todoist_create_task`

**Labels Parameter:**

- Must be list of strings if provided
- Each label should be non-empty string
- Optional parameter
- Used in: `todoist_create_task`, `todoist_update_task`

**Content Parameter:**

- Must be non-empty string
- Required parameter
- Used in: `todoist_create_task`

**Label Filter Parameter:**

- Must be non-empty string if provided
- Optional parameter
- Used in: `todoist_get_tasks`

### Testing Infrastructure

**File:** `tests/test_server.py`

Current test coverage:

- Success path tests: ✓ (15 tests)
- Error handling tests: ✓ (7 tests)
- **Validation tests: ✗ (MISSING)**

Need to add validation test cases for:

- Each parameter type (priority, task_id, labels, etc.)
- Each validation rule (range checks, non-empty checks, type checks)
- Edge cases (boundary values, empty strings, wrong types)

**File:** `tests/conftest.py`

Current fixtures:

- `mock_api_token` - Sets test token
- `mock_task`, `mock_project`, `mock_label` - Mock data builders
- `create_async_gen_mock` - Async generator helper

**No additional fixtures needed** - existing structure supports validation tests.

## Solution Design

### Approach

Add validation functions that check input parameters **before** any API calls and return clear error messages. This approach:

1. **Validates early** - Check parameters before expensive API calls
2. **Centralizes validation logic** - Reusable validation functions
3. **Provides clear feedback** - User-friendly error messages
4. **Maintains consistency** - Same validation style across all tools
5. **Testable** - Validation logic can be unit tested independently

### Implementation Strategy

**Phase 1: Create Validation Helper Functions**

Create reusable validation functions at the top of `server.py`:

```python
def validate_priority(priority: Optional[int]) -> Optional[str]:
    """Validate priority parameter (1-4).

    Returns:
        Error message if invalid, None if valid
    """
    if priority is not None:
        if not isinstance(priority, int):
            return f"Error: Priority must be an integer (received: {type(priority).__name__})"
        if not (1 <= priority <= 4):
            return f"Error: Priority must be between 1 and 4 (received: {priority})"
    return None

def validate_task_id(task_id: str) -> Optional[str]:
    """Validate task_id parameter (non-empty string).

    Returns:
        Error message if invalid, None if valid
    """
    if not task_id or not task_id.strip():
        return "Error: Task ID is required and cannot be empty"
    return None

def validate_project_id(project_id: Optional[str]) -> Optional[str]:
    """Validate project_id parameter (non-empty string if provided).

    Returns:
        Error message if invalid, None if valid
    """
    if project_id is not None and (not project_id or not project_id.strip()):
        return "Error: Project ID cannot be empty"
    return None

def validate_labels(labels: Optional[List[str]]) -> Optional[str]:
    """Validate labels parameter (list of non-empty strings).

    Returns:
        Error message if invalid, None if valid
    """
    if labels is not None:
        if not isinstance(labels, list):
            return f"Error: Labels must be a list (received: {type(labels).__name__})"
        for idx, label in enumerate(labels):
            if not isinstance(label, str):
                return f"Error: Label at index {idx} must be a string (received: {type(label).__name__})"
            if not label or not label.strip():
                return f"Error: Label at index {idx} cannot be empty"
    return None

def validate_non_empty_string(value: str, param_name: str) -> Optional[str]:
    """Validate that a required string parameter is non-empty.

    Returns:
        Error message if invalid, None if valid
    """
    if not value or not value.strip():
        return f"Error: {param_name} is required and cannot be empty"
    return None
```

**Phase 2: Add Validation to Each Tool**

For each tool function, add validation calls at the beginning:

```python
@mcp.tool()
async def todoist_create_task(
    content: str,
    description: Optional[str] = None,
    project_id: Optional[str] = None,
    due_string: Optional[str] = None,
    priority: Optional[int] = None,
    labels: Optional[List[str]] = None,
) -> str:
    """Create a new task in Todoist."""
    # Validation
    if error := validate_non_empty_string(content, "Content"):
        return error
    if error := validate_priority(priority):
        return error
    if error := validate_project_id(project_id):
        return error
    if error := validate_labels(labels):
        return error

    try:
        # ... existing implementation
```

**Phase 3: Add Comprehensive Validation Tests**

Add test cases for each validation scenario in `tests/test_server.py`.

### Benefits

**For Users:**

- Clear, actionable error messages
- Immediate feedback without API delay
- Guidance on how to fix invalid input
- Better developer experience

**For Development:**

- Easier to debug issues
- Reduced API costs (fewer invalid requests)
- Consistent error handling
- Better test coverage

**For Maintenance:**

- Centralized validation logic
- Easy to update validation rules
- Self-documenting parameter constraints
- Prevents API changes from causing confusion

## Implementation Plan

### Step 1: Create Validation Helper Functions

**File:** `src/todoist_mcp/server.py`

**Changes:**

Add validation helper functions after imports, before the MCP server initialization (after line 25):

```python
# Validation helper functions

def validate_priority(priority: Optional[int]) -> Optional[str]:
    """Validate priority parameter (1-4).

    Args:
        priority: Priority value to validate (1=normal, 2=medium, 3=high, 4=urgent)

    Returns:
        Error message if invalid, None if valid
    """
    if priority is not None:
        if not isinstance(priority, int):
            return f"Error: Priority must be an integer (received: {type(priority).__name__})"
        if not (1 <= priority <= 4):
            return f"Error: Priority must be between 1 and 4 (received: {priority})"
    return None


def validate_task_id(task_id: str) -> Optional[str]:
    """Validate task_id parameter (non-empty string).

    Args:
        task_id: Task ID to validate

    Returns:
        Error message if invalid, None if valid
    """
    if not task_id or not task_id.strip():
        return "Error: Task ID is required and cannot be empty"
    return None


def validate_project_id(project_id: Optional[str]) -> Optional[str]:
    """Validate project_id parameter (non-empty string if provided).

    Args:
        project_id: Project ID to validate

    Returns:
        Error message if invalid, None if valid
    """
    if project_id is not None and (not project_id or not project_id.strip()):
        return "Error: Project ID cannot be empty"
    return None


def validate_labels(labels: Optional[List[str]]) -> Optional[str]:
    """Validate labels parameter (list of non-empty strings).

    Args:
        labels: List of label names to validate

    Returns:
        Error message if invalid, None if valid
    """
    if labels is not None:
        if not isinstance(labels, list):
            return f"Error: Labels must be a list (received: {type(labels).__name__})"
        for idx, label in enumerate(labels):
            if not isinstance(label, str):
                return f"Error: Label at index {idx} must be a string (received: {type(label).__name__})"
            if not label or not label.strip():
                return f"Error: Label at index {idx} cannot be empty"
    return None


def validate_non_empty_string(value: str, param_name: str) -> Optional[str]:
    """Validate that a required string parameter is non-empty.

    Args:
        value: String value to validate
        param_name: Name of the parameter (for error message)

    Returns:
        Error message if invalid, None if valid
    """
    if not value or not value.strip():
        return f"Error: {param_name} is required and cannot be empty"
    return None
```

**Testing:**

```bash
# Import and verify functions exist
python -c "from todoist_mcp.server import validate_priority, validate_task_id, validate_project_id, validate_labels, validate_non_empty_string; print('Validation functions imported successfully')"
```

### Step 2: Add Validation to todoist_get_tasks

**File:** `src/todoist_mcp/server.py`

**Changes:**

Add validation at the beginning of `todoist_get_tasks` function (after line 41):

```python
@mcp.tool()
async def todoist_get_tasks(
    project_id: Optional[str] = None,
    label: Optional[str] = None,
) -> str:
    """Get tasks from Todoist with optional filtering."""
    # Validation
    if error := validate_project_id(project_id):
        return error
    if label is not None and (not label or not label.strip()):
        return "Error: Label filter cannot be empty"

    try:
        # ... existing implementation
```

**Testing:**

```bash
# Run tests to ensure no regressions
pytest tests/test_server.py::test_todoist_get_tasks_success -v
pytest tests/test_server.py::test_todoist_get_tasks_empty -v
pytest tests/test_server.py::test_todoist_get_tasks_with_label -v
```

### Step 3: Add Validation to todoist_create_task

**File:** `src/todoist_mcp/server.py`

**Changes:**

Add validation at the beginning of `todoist_create_task` function (after line 96):

```python
@mcp.tool()
async def todoist_create_task(
    content: str,
    description: Optional[str] = None,
    project_id: Optional[str] = None,
    due_string: Optional[str] = None,
    priority: Optional[int] = None,
    labels: Optional[List[str]] = None,
) -> str:
    """Create a new task in Todoist."""
    # Validation
    if error := validate_non_empty_string(content, "Content"):
        return error
    if error := validate_priority(priority):
        return error
    if error := validate_project_id(project_id):
        return error
    if error := validate_labels(labels):
        return error

    try:
        # ... existing implementation
```

**Testing:**

```bash
pytest tests/test_server.py::test_todoist_create_task_success -v
pytest tests/test_server.py::test_todoist_create_task_with_all_params -v
```

### Step 4: Add Validation to todoist_update_task

**File:** `src/todoist_mcp/server.py`

**Changes:**

Add validation at the beginning of `todoist_update_task` function (after line 132):

```python
@mcp.tool()
async def todoist_update_task(
    task_id: str,
    content: Optional[str] = None,
    description: Optional[str] = None,
    due_string: Optional[str] = None,
    priority: Optional[int] = None,
    labels: Optional[List[str]] = None,
) -> str:
    """Update an existing task in Todoist."""
    # Validation
    if error := validate_task_id(task_id):
        return error
    if error := validate_priority(priority):
        return error
    if error := validate_labels(labels):
        return error

    try:
        # ... existing implementation
```

**Testing:**

```bash
pytest tests/test_server.py::test_todoist_update_task_success -v
pytest tests/test_server.py::test_todoist_update_task_multiple_fields -v
```

### Step 5: Add Validation to todoist_complete_task

**File:** `src/todoist_mcp/server.py`

**Changes:**

Add validation at the beginning of `todoist_complete_task` function (after line 159):

```python
@mcp.tool()
async def todoist_complete_task(task_id: str) -> str:
    """Mark a task as complete in Todoist."""
    # Validation
    if error := validate_task_id(task_id):
        return error

    try:
        # ... existing implementation
```

**Testing:**

```bash
pytest tests/test_server.py::test_todoist_complete_task_success -v
```

### Step 6: Add Validation to todoist_delete_task

**File:** `src/todoist_mcp/server.py`

**Changes:**

Add validation at the beginning of `todoist_delete_task` function (after line 179):

```python
@mcp.tool()
async def todoist_delete_task(task_id: str) -> str:
    """Delete a task from Todoist permanently."""
    # Validation
    if error := validate_task_id(task_id):
        return error

    try:
        # ... existing implementation
```

**Testing:**

```bash
pytest tests/test_server.py::test_todoist_delete_task_success -v
```

### Step 7: Add Validation Error Tests - Priority

**File:** `tests/test_server.py`

**Changes:**

Add new test section at the end of the file for validation tests:

```python
# Validation error tests


@pytest.mark.asyncio
async def test_create_task_invalid_priority_out_of_range(mock_api_token):
    """Test todoist_create_task with priority out of range"""
    from todoist_mcp.server import todoist_create_task

    result = await todoist_create_task(content="Test task", priority=5)

    assert result == "Error: Priority must be between 1 and 4 (received: 5)"


@pytest.mark.asyncio
async def test_create_task_invalid_priority_zero(mock_api_token):
    """Test todoist_create_task with priority zero"""
    from todoist_mcp.server import todoist_create_task

    result = await todoist_create_task(content="Test task", priority=0)

    assert result == "Error: Priority must be between 1 and 4 (received: 0)"


@pytest.mark.asyncio
async def test_create_task_invalid_priority_negative(mock_api_token):
    """Test todoist_create_task with negative priority"""
    from todoist_mcp.server import todoist_create_task

    result = await todoist_create_task(content="Test task", priority=-1)

    assert result == "Error: Priority must be between 1 and 4 (received: -1)"


@pytest.mark.asyncio
async def test_update_task_invalid_priority(mock_api_token):
    """Test todoist_update_task with invalid priority"""
    from todoist_mcp.server import todoist_update_task

    result = await todoist_update_task(task_id="12345", priority=10)

    assert result == "Error: Priority must be between 1 and 4 (received: 10)"
```

**Testing:**

```bash
pytest tests/test_server.py -k "invalid_priority" -v
```

### Step 8: Add Validation Error Tests - Task ID

**File:** `tests/test_server.py`

**Changes:**

Add task ID validation tests:

```python
@pytest.mark.asyncio
async def test_update_task_empty_task_id(mock_api_token):
    """Test todoist_update_task with empty task_id"""
    from todoist_mcp.server import todoist_update_task

    result = await todoist_update_task(task_id="", content="Updated")

    assert result == "Error: Task ID is required and cannot be empty"


@pytest.mark.asyncio
async def test_update_task_whitespace_task_id(mock_api_token):
    """Test todoist_update_task with whitespace-only task_id"""
    from todoist_mcp.server import todoist_update_task

    result = await todoist_update_task(task_id="   ", content="Updated")

    assert result == "Error: Task ID is required and cannot be empty"


@pytest.mark.asyncio
async def test_complete_task_empty_task_id(mock_api_token):
    """Test todoist_complete_task with empty task_id"""
    from todoist_mcp.server import todoist_complete_task

    result = await todoist_complete_task(task_id="")

    assert result == "Error: Task ID is required and cannot be empty"


@pytest.mark.asyncio
async def test_delete_task_empty_task_id(mock_api_token):
    """Test todoist_delete_task with empty task_id"""
    from todoist_mcp.server import todoist_delete_task

    result = await todoist_delete_task(task_id="")

    assert result == "Error: Task ID is required and cannot be empty"
```

**Testing:**

```bash
pytest tests/test_server.py -k "empty_task_id or whitespace_task_id" -v
```

### Step 9: Add Validation Error Tests - Project ID & Labels

**File:** `tests/test_server.py`

**Changes:**

Add project ID and labels validation tests:

```python
@pytest.mark.asyncio
async def test_get_tasks_empty_project_id(mock_api_token):
    """Test todoist_get_tasks with empty project_id"""
    from todoist_mcp.server import todoist_get_tasks

    result = await todoist_get_tasks(project_id="")

    assert result == "Error: Project ID cannot be empty"


@pytest.mark.asyncio
async def test_get_tasks_empty_label_filter(mock_api_token):
    """Test todoist_get_tasks with empty label filter"""
    from todoist_mcp.server import todoist_get_tasks

    result = await todoist_get_tasks(label="")

    assert result == "Error: Label filter cannot be empty"


@pytest.mark.asyncio
async def test_create_task_empty_project_id(mock_api_token):
    """Test todoist_create_task with empty project_id"""
    from todoist_mcp.server import todoist_create_task

    result = await todoist_create_task(content="Test", project_id="")

    assert result == "Error: Project ID cannot be empty"


@pytest.mark.asyncio
async def test_create_task_empty_content(mock_api_token):
    """Test todoist_create_task with empty content"""
    from todoist_mcp.server import todoist_create_task

    result = await todoist_create_task(content="")

    assert result == "Error: Content is required and cannot be empty"


@pytest.mark.asyncio
async def test_create_task_whitespace_content(mock_api_token):
    """Test todoist_create_task with whitespace-only content"""
    from todoist_mcp.server import todoist_create_task

    result = await todoist_create_task(content="   ")

    assert result == "Error: Content is required and cannot be empty"


@pytest.mark.asyncio
async def test_create_task_invalid_labels_not_list(mock_api_token):
    """Test todoist_create_task with labels as string instead of list"""
    from todoist_mcp.server import todoist_create_task

    # Note: This test may need to be adjusted based on how FastMCP handles type coercion
    # If FastMCP converts single strings to lists automatically, this test would be different
    result = await todoist_create_task(content="Test", labels="urgent")

    assert "Error: Labels must be a list" in result


@pytest.mark.asyncio
async def test_create_task_labels_with_empty_string(mock_api_token):
    """Test todoist_create_task with empty string in labels list"""
    from todoist_mcp.server import todoist_create_task

    result = await todoist_create_task(content="Test", labels=["urgent", "", "work"])

    assert "Error: Label at index 1 cannot be empty" in result


@pytest.mark.asyncio
async def test_update_task_invalid_labels(mock_api_token):
    """Test todoist_update_task with invalid labels"""
    from todoist_mcp.server import todoist_update_task

    result = await todoist_update_task(task_id="12345", labels=["", "work"])

    assert "Error: Label at index 0 cannot be empty" in result
```

**Testing:**

```bash
pytest tests/test_server.py -k "empty_project_id or empty_label or empty_content or invalid_labels" -v
```

### Step 10: Run Full Test Suite and Verify Coverage

**Commands:**

```bash
# Run all tests
pytest tests/test_server.py -v

# Run with coverage report
pytest tests/test_server.py --cov=src/todoist_mcp --cov-report=term-missing --cov-report=html -v

# Run only validation tests
pytest tests/test_server.py -k "invalid or empty" -v
```

**Expected Results:**

- All existing tests continue to pass (25 tests)
- All new validation tests pass (~16 new tests)
- Total: ~41 tests passing
- Coverage remains >90% (should improve slightly)
- No uncovered validation code

**Verify:**

1. Check coverage report for validation functions
2. Verify all validation paths are tested
3. Review HTML coverage report: `open htmlcov/index.html`

### Step 11: Update Documentation

**File:** `README.md` (if exists) or create `docs/validation.md`

**Changes:**

Document parameter validation rules for users:

```markdown
## Parameter Validation

All MCP tools validate input parameters before making API calls. Invalid parameters return clear error messages.

### Priority (1-4)

Used in: `todoist_create_task`, `todoist_update_task`

- **Valid values:** 1 (normal), 2 (medium), 3 (high), 4 (urgent)
- **Error message:** "Error: Priority must be between 1 and 4 (received: X)"

### Task ID (required)

Used in: `todoist_update_task`, `todoist_complete_task`, `todoist_delete_task`

- **Valid values:** Non-empty string
- **Error message:** "Error: Task ID is required and cannot be empty"

### Project ID (optional)

Used in: `todoist_get_tasks`, `todoist_create_task`

- **Valid values:** Non-empty string if provided
- **Error message:** "Error: Project ID cannot be empty"

### Labels (optional)

Used in: `todoist_create_task`, `todoist_update_task`

- **Valid values:** List of non-empty strings
- **Error messages:**
  - "Error: Labels must be a list (received: X)"
  - "Error: Label at index N must be a string (received: X)"
  - "Error: Label at index N cannot be empty"

### Content (required)

Used in: `todoist_create_task`

- **Valid values:** Non-empty string
- **Error message:** "Error: Content is required and cannot be empty"
```

## Testing Strategy

### Unit Testing - Validation Functions

**Test each validation function independently:**

1. **validate_priority()**
   - Valid: None, 1, 2, 3, 4
   - Invalid: 0, 5, -1, 100, "string"
   - Edge cases: boundary values (1, 4)

2. **validate_task_id()**
   - Valid: "12345", "task_id_123"
   - Invalid: "", "   ", None (if applicable)

3. **validate_project_id()**
   - Valid: None, "67890", "project_123"
   - Invalid: "", "   "

4. **validate_labels()**
   - Valid: None, [], ["urgent"], ["urgent", "work"]
   - Invalid: "string", ["", "work"], [123, "work"], ["  "]

5. **validate_non_empty_string()**
   - Valid: "test", "  test  "
   - Invalid: "", "   ", None

### Integration Testing - Tool Functions

**Test each tool with invalid parameters:**

1. **todoist_get_tasks**
   - Empty project_id
   - Empty label filter
   - Whitespace-only values

2. **todoist_create_task**
   - Empty content
   - Invalid priority (0, 5, -1)
   - Empty project_id
   - Invalid labels (not list, empty strings)

3. **todoist_update_task**
   - Empty task_id
   - Invalid priority
   - Invalid labels

4. **todoist_complete_task**
   - Empty task_id

5. **todoist_delete_task**
   - Empty task_id

### Regression Testing

**Ensure existing functionality still works:**

- All 25 existing tests must continue to pass
- Success path tests verify validation doesn't break normal flow
- Error handling tests verify API errors still caught

### Edge Cases

**Test boundary conditions:**

- Priority: 1 (valid min), 4 (valid max), 0 (invalid), 5 (invalid)
- Empty strings: "", "   ", "\t\n"
- Labels: empty list [], single item ["urgent"], multiple ["a", "b", "c"]
- Whitespace: leading/trailing spaces in strings

## Success Criteria

- [ ] All validation helper functions created (5 functions)
- [ ] Validation added to todoist_get_tasks
- [ ] Validation added to todoist_create_task
- [ ] Validation added to todoist_update_task
- [ ] Validation added to todoist_complete_task
- [ ] Validation added to todoist_delete_task
- [ ] Validation error tests for priority parameter (~4 tests)
- [ ] Validation error tests for task_id parameter (~4 tests)
- [ ] Validation error tests for project_id parameter (~3 tests)
- [ ] Validation error tests for labels parameter (~3 tests)
- [ ] Validation error tests for content parameter (~2 tests)
- [ ] All existing tests still pass (25 tests)
- [ ] All new validation tests pass (~16 tests)
- [ ] Code coverage remains >90%
- [ ] Clear error messages returned for all validation failures
- [ ] Documentation updated with parameter constraints
- [ ] No regressions in existing functionality

## Files Modified

1. `src/todoist_mcp/server.py`
   - Add 5 validation helper functions
   - Add validation to 5 tool functions (get_tasks, create_task, update_task, complete_task, delete_task)

2. `tests/test_server.py`
   - Add ~16 new validation error tests
   - Organize tests with clear section for validation tests

3. `README.md` or `docs/validation.md`
   - Document parameter validation rules
   - Provide examples of error messages

## Related Issues and Tasks

### Depends On

- Issue #4 (Add proper unit tests) - ✓ Complete
  - Testing infrastructure in place
  - Mock fixtures ready
  - High test coverage established

### Blocks

- Improved user experience
- Clearer debugging for integration issues
- API documentation accuracy

### Related

- Future: Add validation for due_string format
- Future: Add validation for description length limits
- Future: Consider adding rate limiting/retry logic

### Enables

- Better error messages in MCP tool responses
- Reduced invalid API calls (cost savings)
- Easier debugging for users
- Foundation for additional validation rules

## References

- [GitHub Issue #5](https://github.com/denhamparry/todoist-mcp/issues/5)
- [Todoist API Documentation](https://developer.todoist.com/rest/v2/)
- [Todoist Priority Mapping](https://developer.todoist.com/rest/v2/#tasks)
  - API uses 1-4 where 4 is most urgent
  - Display as P1 (Urgent), P2 (High), P3 (Medium), P4 (Normal)
- Current server implementation: `src/todoist_mcp/server.py`
- Current test suite: `tests/test_server.py`
- Issue #4 plan: `docs/plan/issues/4_add_proper_unit_tests_with_mocked_success_scenarios.md`

## Notes

### Key Insights

1. **Validation should happen before API calls** - Save network round-trip and provide faster feedback
2. **Error messages must be user-friendly** - Include parameter name, received value, and valid range
3. **Centralized validation functions** - Avoid code duplication across tools
4. **Walrus operator** - Python 3.8+ allows `if error := validate_x()` for concise validation
5. **Type coercion concerns** - FastMCP may handle some type conversions automatically (need to test)
6. **Optional vs Required** - Clear distinction in validation (None allowed vs must have value)

### Alternative Approaches Considered

1. **Pydantic models for validation** - More robust but heavier dependency ❌
   - Pros: Built-in validation, type checking, data models
   - Cons: Additional dependency, more complex setup, overkill for simple validation

2. **Decorator-based validation** - Clean separation but more complex ❌
   - Pros: Clean separation of concerns, reusable decorators
   - Cons: More abstract, harder to debug, less explicit

3. **Inline validation** - Validation directly in each function ❌
   - Pros: Simple, explicit
   - Cons: Code duplication, harder to maintain, inconsistent messages

4. **Helper functions (chosen approach)** - Balance of simplicity and reusability ✅
   - Pros: Reusable, testable, clear error messages, easy to maintain
   - Cons: Small amount of boilerplate

### Best Practices

**Error Message Format:**

- Start with "Error: " prefix for clarity
- Include parameter name
- Show received value (when helpful)
- Indicate valid range/format

**Validation Order:**

- Validate required parameters first
- Validate type before value range
- Validate structure before content
- Return immediately on first error

**Testing:**

- Test both valid and invalid cases
- Test boundary values (1, 4 for priority)
- Test edge cases (empty, whitespace, None)
- Test type mismatches where possible

**Code Organization:**

- Group validation functions together
- Document validation logic in docstrings
- Keep validation separate from business logic
- Use consistent return patterns (None = valid, str = error)

### Monitoring

**After implementation, monitor:**

- Frequency of validation errors (which parameters fail most often)
- User feedback on error message clarity
- Any missed validation cases (new edge cases discovered)
- Performance impact of validation (should be negligible)
