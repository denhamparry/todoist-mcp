# GitHub Issue #4: Add proper unit tests with mocked success scenarios

**Issue:** [#4](https://github.com/denhamparry/todoist-mcp/issues/4)
**Status:** Open
**Labels:** bug
**Priority:** HIGH
**Date:** 2025-11-27

## Problem Statement

Currently, the test suite lacks comprehensive unit tests with properly mocked success scenarios for all MCP tools. The existing tests in `tests/test_server.py` only validate that functions return strings and expect authentication errors. This means success paths are not properly tested without requiring a real API token, making tests dependent on external services and unable to verify correct response formatting.

### Current Behavior

The current test suite (tests/test_server.py:38-104):

- Tests only verify return types (strings)
- Expects API authentication failures
- Doesn't test success scenarios with valid responses
- Cannot verify response formatting matches expected output
- Cannot ensure user-friendly success messages are returned
- Requires actual API calls which may fail due to network/authentication issues

Example current test:

```python
@pytest.mark.asyncio
async def test_todoist_get_tasks_returns_string(mock_api_token):
    """Test that todoist_get_tasks returns a string"""
    from todoist_mcp.server import todoist_get_tasks

    # This will fail with auth error but should return error string
    result = await todoist_get_tasks()
    assert isinstance(result, str)
```

### Expected Behavior

Tests should:

- Mock Todoist API HTTP endpoints using `pytest-httpx`
- Test happy path scenarios with successful API responses
- Verify response formatting matches expected MCP tool output
- Ensure all tools return user-friendly success messages
- Run independently without requiring real API tokens
- Achieve >90% test coverage for success paths

## Current State Analysis

### Test Infrastructure

**File:** `tests/conftest.py`

Current fixtures:

- `mock_api_token` - Sets environment variable for API token (lines 10-13)
- `todoist_client` - Creates real API client (skips if no token) (lines 17-22)
- `test_project_id` - Gets test project ID from environment (lines 26-31)

**Missing:**

- HTTP mocking fixtures using `pytest-httpx`
- Mock response builders for Todoist API objects
- Fixture for mocking successful API responses

### Server Implementation

**File:** `src/todoist_mcp/server.py`

7 MCP tools that need comprehensive testing:

1. `todoist_get_tasks` (lines 28-62) - Returns formatted task list
2. `todoist_create_task` (lines 65-98) - Returns success message with task ID
3. `todoist_update_task` (lines 101-137) - Returns success message
4. `todoist_complete_task` (lines 140-157) - Returns completion confirmation
5. `todoist_delete_task` (lines 160-177) - Returns deletion confirmation
6. `todoist_get_projects` (lines 180-201) - Returns formatted project list
7. `todoist_get_labels` (lines 204-223) - Returns formatted label list

Each tool:

- Uses `TodoistAPIAsync` client to make HTTP calls
- Returns formatted string responses
- Includes error handling with string error messages
- Uses success indicators (✓) in messages

### Dependencies

**File:** `pyproject.toml`

Testing dependencies:

- `pytest>=8.0.0` - Test framework ✓
- `pytest-asyncio>=0.23.0` - Async test support ✓
- `pytest-cov>=4.1.0` - Coverage reporting ✓
- `pytest-httpx>=0.30.0` - HTTP mocking ✓ (already in dependencies!)

External API client:

- `todoist-api-python>=2.1.9` - Uses httpx under the hood

### Test Coverage Gap

Current `tests/test_server.py` covers:

- Server initialization (lines 8-34)
- Return type validation (lines 37-104)
- Main function existence (lines 107-111)

**Missing coverage:**

- Success response parsing
- Response formatting verification
- Edge cases (empty lists, missing fields)
- All tool parameters and optional arguments
- Priority mapping logic (line 53)
- Label/due date formatting

## Solution Design

### Approach

Use `pytest-httpx` to mock HTTP requests made by the `TodoistAPIAsync` client, allowing us to test success scenarios without real API calls. This approach:

1. **Intercepts HTTP calls** - `pytest-httpx` mocks httpx requests at the transport layer
2. **Returns mock responses** - We control the exact JSON responses from "Todoist API"
3. **Tests formatting logic** - Verifies our tools format responses correctly
4. **Validates messages** - Ensures user-friendly success messages
5. **Runs offline** - No network dependency, fast and reliable tests

### Implementation Strategy

**Phase 1: Setup Mock Infrastructure**

- Create `pytest-httpx` fixtures in conftest.py
- Build helper functions for common mock responses
- Create mock data factories for tasks, projects, labels

**Phase 2: Add Success Path Tests**

- Test each of the 7 MCP tools with mocked successful responses
- Cover main parameters and optional arguments
- Verify formatted output strings
- Test edge cases (empty results, missing optional fields)

**Phase 3: Verify Coverage**

- Run pytest with coverage report
- Ensure >90% coverage for success paths
- Fill any gaps in test coverage

### Mock Response Examples

**Todoist Task Object:**

```python
{
    "id": "12345",
    "content": "Test task",
    "description": "Task description",
    "project_id": "67890",
    "due": {"string": "tomorrow", "date": "2025-11-28"},
    "priority": 4,
    "labels": ["urgent", "work"]
}
```

**Todoist Project Object:**

```python
{
    "id": "67890",
    "name": "Work Project",
    "is_favorite": true
}
```

**Todoist Label Object:**

```python
{
    "id": "11111",
    "name": "urgent"
}
```

### Benefits

- **Reliable tests** - No dependency on external API availability
- **Fast execution** - No network latency
- **Comprehensive coverage** - Can test all scenarios including edge cases
- **Clear expectations** - Validates exact response formatting
- **CI/CD friendly** - Tests run without API tokens in CI environment
- **Regression prevention** - Catches formatting changes in future updates

## Implementation Plan

### Step 1: Enhance Test Fixtures

**File:** `tests/conftest.py`

**Changes:**

- Add `httpx_mock` fixture import from `pytest_httpx`
- Create mock data builder functions for Todoist objects
- Add helper fixture for mocking successful API responses

**Example:**

```python
import pytest
from pytest_httpx import HTTPXMock

@pytest.fixture
def mock_task():
    """Create a mock Todoist task object"""
    return {
        "id": "12345",
        "content": "Test task",
        "description": "Test description",
        "project_id": "67890",
        "due": {"string": "tomorrow", "date": "2025-11-28"},
        "priority": 4,
        "labels": ["urgent", "work"],
    }

@pytest.fixture
def mock_project():
    """Create a mock Todoist project object"""
    return {
        "id": "67890",
        "name": "Test Project",
        "is_favorite": True,
    }

@pytest.fixture
def mock_label():
    """Create a mock Todoist label object"""
    return {
        "id": "11111",
        "name": "urgent",
    }
```

**Testing:**

```bash
pytest tests/conftest.py -v
```

### Step 2: Add Success Tests for todoist_get_tasks

**File:** `tests/test_server.py`

**Changes:**

- Add new test function `test_todoist_get_tasks_success`
- Mock GET request to `/rest/v2/tasks`
- Verify formatted output includes task details

**Example:**

```python
@pytest.mark.asyncio
async def test_todoist_get_tasks_success(mock_api_token, httpx_mock, mock_task):
    """Test todoist_get_tasks with successful API response"""
    # Mock the API endpoint
    httpx_mock.add_response(
        url="https://api.todoist.com/rest/v2/tasks",
        json=[mock_task],
        status_code=200,
    )

    from todoist_mcp.server import todoist_get_tasks

    result = await todoist_get_tasks()

    # Verify response format
    assert "Found 1 task(s):" in result
    assert "[12345] Test task" in result
    assert "Due: tomorrow" in result
    assert "Priority: P1 (Urgent)" in result
    assert "Labels: urgent, work" in result

@pytest.mark.asyncio
async def test_todoist_get_tasks_empty(mock_api_token, httpx_mock):
    """Test todoist_get_tasks with no tasks"""
    httpx_mock.add_response(
        url="https://api.todoist.com/rest/v2/tasks",
        json=[],
        status_code=200,
    )

    from todoist_mcp.server import todoist_get_tasks

    result = await todoist_get_tasks()
    assert result == "No tasks found."

@pytest.mark.asyncio
async def test_todoist_get_tasks_with_filter(mock_api_token, httpx_mock, mock_task):
    """Test todoist_get_tasks with filter parameter"""
    httpx_mock.add_response(
        url="https://api.todoist.com/rest/v2/tasks?filter=today",
        json=[mock_task],
        status_code=200,
    )

    from todoist_mcp.server import todoist_get_tasks

    result = await todoist_get_tasks(filter="today")
    assert "Found 1 task(s):" in result
```

**Testing:**

```bash
pytest tests/test_server.py::test_todoist_get_tasks_success -v
pytest tests/test_server.py::test_todoist_get_tasks_empty -v
pytest tests/test_server.py::test_todoist_get_tasks_with_filter -v
```

### Step 3: Add Success Tests for todoist_create_task

**File:** `tests/test_server.py`

**Changes:**

- Add test for task creation with mocked POST response
- Test with minimal and full parameters
- Verify success message format

**Example:**

```python
@pytest.mark.asyncio
async def test_todoist_create_task_success(mock_api_token, httpx_mock, mock_task):
    """Test todoist_create_task with successful API response"""
    httpx_mock.add_response(
        url="https://api.todoist.com/rest/v2/tasks",
        method="POST",
        json=mock_task,
        status_code=200,
    )

    from todoist_mcp.server import todoist_create_task

    result = await todoist_create_task(content="Test task")

    assert result == "✓ Task created: Test task (ID: 12345)"

@pytest.mark.asyncio
async def test_todoist_create_task_with_all_params(mock_api_token, httpx_mock, mock_task):
    """Test todoist_create_task with all parameters"""
    httpx_mock.add_response(
        url="https://api.todoist.com/rest/v2/tasks",
        method="POST",
        json=mock_task,
        status_code=200,
    )

    from todoist_mcp.server import todoist_create_task

    result = await todoist_create_task(
        content="Test task",
        description="Test description",
        project_id="67890",
        due_string="tomorrow",
        priority=4,
        labels=["urgent", "work"]
    )

    assert "✓ Task created:" in result
    assert "12345" in result
```

**Testing:**

```bash
pytest tests/test_server.py::test_todoist_create_task_success -v
pytest tests/test_server.py::test_todoist_create_task_with_all_params -v
```

### Step 4: Add Success Tests for todoist_update_task

**File:** `tests/test_server.py`

**Changes:**

- Add test for task update with mocked POST response
- Test various update scenarios (content, priority, labels)
- Verify success message

**Example:**

```python
@pytest.mark.asyncio
async def test_todoist_update_task_success(mock_api_token, httpx_mock):
    """Test todoist_update_task with successful API response"""
    httpx_mock.add_response(
        url="https://api.todoist.com/rest/v2/tasks/12345",
        method="POST",
        json={"success": True},
        status_code=204,
    )

    from todoist_mcp.server import todoist_update_task

    result = await todoist_update_task(task_id="12345", content="Updated task")

    assert result == "✓ Task 12345 updated successfully"

@pytest.mark.asyncio
async def test_todoist_update_task_multiple_fields(mock_api_token, httpx_mock):
    """Test updating multiple fields at once"""
    httpx_mock.add_response(
        url="https://api.todoist.com/rest/v2/tasks/12345",
        method="POST",
        json={"success": True},
        status_code=204,
    )

    from todoist_mcp.server import todoist_update_task

    result = await todoist_update_task(
        task_id="12345",
        content="Updated",
        priority=3,
        labels=["important"]
    )

    assert "✓ Task 12345 updated successfully" in result
```

**Testing:**

```bash
pytest tests/test_server.py::test_todoist_update_task_success -v
pytest tests/test_server.py::test_todoist_update_task_multiple_fields -v
```

### Step 5: Add Success Tests for todoist_complete_task

**File:** `tests/test_server.py`

**Changes:**

- Add test for task completion with mocked POST response
- Verify success message format

**Example:**

```python
@pytest.mark.asyncio
async def test_todoist_complete_task_success(mock_api_token, httpx_mock):
    """Test todoist_complete_task with successful API response"""
    httpx_mock.add_response(
        url="https://api.todoist.com/rest/v2/tasks/12345/close",
        method="POST",
        json={"success": True},
        status_code=204,
    )

    from todoist_mcp.server import todoist_complete_task

    result = await todoist_complete_task(task_id="12345")

    assert result == "✓ Task 12345 marked as complete"
```

**Testing:**

```bash
pytest tests/test_server.py::test_todoist_complete_task_success -v
```

### Step 6: Add Success Tests for todoist_delete_task

**File:** `tests/test_server.py`

**Changes:**

- Add test for task deletion with mocked DELETE response
- Verify success message format

**Example:**

```python
@pytest.mark.asyncio
async def test_todoist_delete_task_success(mock_api_token, httpx_mock):
    """Test todoist_delete_task with successful API response"""
    httpx_mock.add_response(
        url="https://api.todoist.com/rest/v2/tasks/12345",
        method="DELETE",
        json={"success": True},
        status_code=204,
    )

    from todoist_mcp.server import todoist_delete_task

    result = await todoist_delete_task(task_id="12345")

    assert result == "✓ Task 12345 deleted"
```

**Testing:**

```bash
pytest tests/test_server.py::test_todoist_delete_task_success -v
```

### Step 7: Add Success Tests for todoist_get_projects

**File:** `tests/test_server.py`

**Changes:**

- Add test for getting projects with mocked GET response
- Test with favorite and non-favorite projects
- Test empty project list
- Verify formatted output

**Example:**

```python
@pytest.mark.asyncio
async def test_todoist_get_projects_success(mock_api_token, httpx_mock, mock_project):
    """Test todoist_get_projects with successful API response"""
    httpx_mock.add_response(
        url="https://api.todoist.com/rest/v2/projects",
        json=[mock_project],
        status_code=200,
    )

    from todoist_mcp.server import todoist_get_projects

    result = await todoist_get_projects()

    assert "Found 1 project(s):" in result
    assert "[67890] Test Project" in result
    assert "⭐ Favorite" in result

@pytest.mark.asyncio
async def test_todoist_get_projects_empty(mock_api_token, httpx_mock):
    """Test todoist_get_projects with no projects"""
    httpx_mock.add_response(
        url="https://api.todoist.com/rest/v2/projects",
        json=[],
        status_code=200,
    )

    from todoist_mcp.server import todoist_get_projects

    result = await todoist_get_projects()
    assert result == "No projects found."

@pytest.mark.asyncio
async def test_todoist_get_projects_non_favorite(mock_api_token, httpx_mock):
    """Test todoist_get_projects with non-favorite project"""
    project = {
        "id": "67890",
        "name": "Regular Project",
        "is_favorite": False,
    }
    httpx_mock.add_response(
        url="https://api.todoist.com/rest/v2/projects",
        json=[project],
        status_code=200,
    )

    from todoist_mcp.server import todoist_get_projects

    result = await todoist_get_projects()

    assert "[67890] Regular Project" in result
    assert "⭐ Favorite" not in result
```

**Testing:**

```bash
pytest tests/test_server.py::test_todoist_get_projects_success -v
pytest tests/test_server.py::test_todoist_get_projects_empty -v
pytest tests/test_server.py::test_todoist_get_projects_non_favorite -v
```

### Step 8: Add Success Tests for todoist_get_labels

**File:** `tests/test_server.py`

**Changes:**

- Add test for getting labels with mocked GET response
- Test empty label list
- Verify formatted output

**Example:**

```python
@pytest.mark.asyncio
async def test_todoist_get_labels_success(mock_api_token, httpx_mock, mock_label):
    """Test todoist_get_labels with successful API response"""
    httpx_mock.add_response(
        url="https://api.todoist.com/rest/v2/labels",
        json=[mock_label],
        status_code=200,
    )

    from todoist_mcp.server import todoist_get_labels

    result = await todoist_get_labels()

    assert "Found 1 label(s):" in result
    assert "[11111] urgent" in result

@pytest.mark.asyncio
async def test_todoist_get_labels_empty(mock_api_token, httpx_mock):
    """Test todoist_get_labels with no labels"""
    httpx_mock.add_response(
        url="https://api.todoist.com/rest/v2/labels",
        json=[],
        status_code=200,
    )

    from todoist_mcp.server import todoist_get_labels

    result = await todoist_get_labels()
    assert result == "No labels found."

@pytest.mark.asyncio
async def test_todoist_get_labels_multiple(mock_api_token, httpx_mock):
    """Test todoist_get_labels with multiple labels"""
    labels = [
        {"id": "11111", "name": "urgent"},
        {"id": "22222", "name": "work"},
        {"id": "33333", "name": "personal"},
    ]
    httpx_mock.add_response(
        url="https://api.todoist.com/rest/v2/labels",
        json=labels,
        status_code=200,
    )

    from todoist_mcp.server import todoist_get_labels

    result = await todoist_get_labels()

    assert "Found 3 label(s):" in result
    assert "[11111] urgent" in result
    assert "[22222] work" in result
    assert "[33333] personal" in result
```

**Testing:**

```bash
pytest tests/test_server.py::test_todoist_get_labels_success -v
pytest tests/test_server.py::test_todoist_get_labels_empty -v
pytest tests/test_server.py::test_todoist_get_labels_multiple -v
```

### Step 9: Run Full Test Suite with Coverage

**Command:**

```bash
pytest tests/test_server.py --cov=src/todoist_mcp --cov-report=term-missing --cov-report=html -v
```

**Expected:**

- All tests pass
- Coverage >90% for success paths
- HTML report generated in `htmlcov/`

**Verify:**

- Check coverage report for any gaps
- Ensure all 7 tools have success path coverage
- Review uncovered lines and add tests if needed

### Step 10: Update Test Documentation

**File:** `tests/test_server.py`

**Changes:**

- Add module docstring explaining test structure
- Document mocking strategy
- Add comments for test organization

**Example:**

```python
"""Unit tests for Todoist MCP Server

Test Structure:
- Server initialization tests (test_server_requires_api_token, test_server_initializes_with_token)
- Success path tests with mocked HTTP responses (using pytest-httpx)
- Edge case tests (empty results, missing fields)
- Error handling tests (existing tests)

Mocking Strategy:
- Uses pytest-httpx to mock HTTP requests to Todoist API
- Mock responses defined in conftest.py fixtures
- Tests verify both successful API calls and response formatting

Coverage Goals:
- >90% coverage for success paths
- All 7 MCP tools tested with mocked responses
- Edge cases covered (empty lists, optional parameters)
"""
```

## Testing Strategy

### Unit Testing

**Approach:**

- Mock all HTTP requests using `pytest-httpx`
- Test each tool function in isolation
- Verify response formatting independently of API

**Test Cases:**

1. **todoist_get_tasks**
   - Success with tasks
   - Empty task list
   - Tasks with all fields populated
   - Tasks with optional fields missing (no due date, no labels)
   - Filter parameter usage
   - Project filter usage

2. **todoist_create_task**
   - Minimal parameters (content only)
   - All parameters provided
   - Natural language due dates

3. **todoist_update_task**
   - Single field update
   - Multiple field updates
   - Each parameter type (content, description, due_string, priority, labels)

4. **todoist_complete_task**
   - Successful completion

5. **todoist_delete_task**
   - Successful deletion

6. **todoist_get_projects**
   - Success with projects
   - Empty project list
   - Favorite projects
   - Non-favorite projects
   - Multiple projects

7. **todoist_get_labels**
   - Success with labels
   - Empty label list
   - Multiple labels

### Integration Testing

**File:** `tests/test_integration.py` (existing, not modified)

Keep existing integration tests that use real API for end-to-end validation when `TODOIST_API_TOKEN` is available.

### Regression Testing

**Existing Functionality:**

- Server initialization tests remain unchanged (tests/test_server.py:8-34)
- Return type validation tests remain as fallback (tests/test_server.py:37-104)
- Main function test remains (tests/test_server.py:107-111)

**Test Execution:**

```bash
# Run all tests
pytest -v

# Run only new success tests
pytest tests/test_server.py -k "success" -v

# Run with coverage
pytest --cov=src/todoist_mcp --cov-report=html

# Run specific tool tests
pytest tests/test_server.py -k "todoist_get_tasks" -v
```

### CI/CD Integration

**Requirements:**

- Tests run without requiring `TODOIST_API_TOKEN`
- Fast execution (no network calls)
- Coverage report generated
- Coverage threshold: 80% (configured in pyproject.toml:36)

**GitHub Actions:**

```yaml
- name: Run tests with coverage
  run: |
    pytest --cov=src/todoist_mcp --cov-report=xml --cov-report=term
```

## Success Criteria

- [x] Issue #4 fetched and analyzed
- [ ] Mock fixtures added to conftest.py for pytest-httpx
- [ ] Success tests added for todoist_get_tasks (3+ test cases)
- [ ] Success tests added for todoist_create_task (2+ test cases)
- [ ] Success tests added for todoist_update_task (2+ test cases)
- [ ] Success tests added for todoist_complete_task (1+ test case)
- [ ] Success tests added for todoist_delete_task (1+ test case)
- [ ] Success tests added for todoist_get_projects (3+ test cases)
- [ ] Success tests added for todoist_get_labels (3+ test cases)
- [ ] All tests pass without requiring real API token
- [ ] Test coverage for success paths >90%
- [ ] All tools return user-friendly success messages (verified in tests)
- [ ] Response formatting verified for all tools
- [ ] Edge cases tested (empty results, missing optional fields)
- [ ] pytest-httpx used for all HTTP mocking
- [ ] Test documentation updated with mocking strategy
- [ ] Coverage report generated and reviewed

## Files Modified

1. `tests/conftest.py` - Add pytest-httpx fixtures and mock data builders
2. `tests/test_server.py` - Add comprehensive success path tests for all 7 tools

## Related Issues and Tasks

### Depends On

- None (pytest-httpx already in dependencies)

### Blocks

- Test coverage reporting accuracy
- CI/CD pipeline stability
- Confidence in response formatting

### Related

- Integration tests in `tests/test_integration.py` (for real API testing)
- Server implementation in `src/todoist_mcp/server.py`

### Enables

- Reliable offline testing
- Faster test execution in CI/CD
- Better regression prevention
- Easier refactoring with test safety net

## References

- [GitHub Issue #4](https://github.com/denhamparry/todoist-mcp/issues/4)
- [pytest-httpx Documentation](https://colin-b.github.io/pytest_httpx/)
- [Todoist REST API v2](https://developer.todoist.com/rest/v2/)
- [todoist-api-python SDK](https://github.com/Doist/todoist-api-python)
- Current test file: `tests/test_server.py`
- Current fixtures: `tests/conftest.py`
- Server implementation: `src/todoist_mcp/server.py`

## Notes

### Key Insights

1. **pytest-httpx is already installed** - Listed in `pyproject.toml` dev dependencies, ready to use
2. **TodoistAPIAsync uses httpx** - The official SDK uses httpx for HTTP requests, making pytest-httpx the perfect choice for mocking
3. **Current tests validate types only** - Need to verify actual response content and formatting
4. **7 tools to test** - Each has different response formats and parameters to verify
5. **Success messages use ✓ symbol** - Tests should verify these user-friendly indicators
6. **Priority mapping logic** - Special attention needed for priority display (P1/P2/P3) in tests

### Alternative Approaches Considered

1. **Mock at Todoist API client level** - Would require patching TodoistAPIAsync, less realistic ❌
2. **Use responses library** - pytest-httpx is more modern and specifically designed for httpx ❌
3. **Use unittest.mock** - More verbose, less declarative than pytest-httpx ❌
4. **pytest-httpx (chosen approach)** - Clean, declarative, specifically for httpx, already in dependencies ✅

### Best Practices

**HTTP Mocking:**

- Use `httpx_mock.add_response()` for each endpoint
- Match exact URLs including query parameters
- Use realistic mock data that matches Todoist API schema
- Test both success and empty result scenarios

**Test Organization:**

- Group tests by tool function
- Name tests clearly: `test_<tool>_<scenario>`
- Use descriptive docstrings
- Keep tests focused on single scenarios

**Coverage Strategy:**

- Aim for >90% coverage on success paths
- Don't sacrifice test quality for coverage percentage
- Focus on meaningful assertions
- Test edge cases and optional parameters

**Maintenance:**

- Keep mock data in fixtures for reusability
- Update tests when API responses change
- Document mocking strategy in test file
- Review coverage reports regularly

**Monitoring:**

- Run tests in CI/CD pipeline
- Generate coverage reports
- Alert on coverage drops
- Review uncovered lines periodically
