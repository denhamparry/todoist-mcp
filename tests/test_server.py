"""Unit tests for Todoist MCP Server

Test Structure:
- Server initialization tests
- Success path tests with mocked API client (using monkeypatch)
- Edge case tests (empty results, missing fields)
- Error handling tests (existing tests)

Mocking Strategy:
- Uses monkeypatch to mock Todoist API client methods
- Mock responses defined in conftest.py fixtures
- Tests verify both successful API calls and response formatting

Coverage Goals:
- >90% coverage for success paths
- All 7 MCP tools tested with mocked responses
- Edge cases covered (empty lists, optional parameters)
"""

import logging
import os
from unittest.mock import patch

import pytest


def test_server_requires_api_token():
    """Test that server raises error without API token"""
    # Remove any existing token
    if "TODOIST_API_TOKEN" in os.environ:
        del os.environ["TODOIST_API_TOKEN"]

    with pytest.raises(ValueError, match="TODOIST_API_TOKEN"):
        # This import will trigger the ValueError
        import importlib

        import todoist_mcp.server as server_module

        importlib.reload(server_module)


def test_server_initializes_with_token(mock_api_token):
    """Test that server initializes properly with token"""
    # Reimport server module with mocked token
    import importlib

    import todoist_mcp.server as server_module

    importlib.reload(server_module)

    assert server_module.mcp is not None
    assert server_module.todoist is not None
    assert server_module.API_TOKEN == "test_token_12345"


@pytest.mark.asyncio
async def test_todoist_get_tasks_returns_string(mock_api_token):
    """Test that todoist_get_tasks returns a string"""
    from todoist_mcp.server import todoist_get_tasks

    # This will fail with auth error but should return error string
    result = await todoist_get_tasks()
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_todoist_create_task_returns_string(mock_api_token):
    """Test that todoist_create_task returns a string"""
    from todoist_mcp.server import todoist_create_task

    # This will fail with auth error but should return error string
    result = await todoist_create_task(content="Test task")
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_todoist_update_task_returns_string(mock_api_token):
    """Test that todoist_update_task returns a string"""
    from todoist_mcp.server import todoist_update_task

    # This will fail with auth error but should return error string
    result = await todoist_update_task(task_id="123", content="Updated")
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_todoist_complete_task_returns_string(mock_api_token):
    """Test that todoist_complete_task returns a string"""
    from todoist_mcp.server import todoist_complete_task

    # This will fail with auth error but should return error string
    result = await todoist_complete_task(task_id="123")
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_todoist_delete_task_returns_string(mock_api_token):
    """Test that todoist_delete_task returns a string"""
    from todoist_mcp.server import todoist_delete_task

    # This will fail with auth error but should return error string
    result = await todoist_delete_task(task_id="123")
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_todoist_get_projects_returns_string(mock_api_token):
    """Test that todoist_get_projects returns a string"""
    from todoist_mcp.server import todoist_get_projects

    # This will fail with auth error but should return error string
    result = await todoist_get_projects()
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_todoist_get_labels_returns_string(mock_api_token):
    """Test that todoist_get_labels returns a string"""
    from todoist_mcp.server import todoist_get_labels

    # This will fail with auth error but should return error string
    result = await todoist_get_labels()
    assert isinstance(result, str)


def test_main_function_exists(mock_api_token):
    """Test that main function exists"""
    from todoist_mcp.server import main

    assert callable(main)


# Success path tests with mocked HTTP responses


@pytest.mark.asyncio
async def test_todoist_get_tasks_success(mock_api_token, monkeypatch, mock_task):
    """Test todoist_get_tasks with successful API response"""
    from todoist_api_python.models import Task

    from tests.conftest import create_async_gen_mock

    # Create Task objects from mock data
    task_obj = Task.from_dict(mock_task)

    # Patch the todoist client's get_tasks method using helper function
    import todoist_mcp.server

    monkeypatch.setattr(
        todoist_mcp.server.todoist, "get_tasks", create_async_gen_mock([task_obj])
    )

    from todoist_mcp.server import todoist_get_tasks

    result = await todoist_get_tasks()

    # Verify response format using partial matches for flexible content
    assert "Found 1 task(s):" in result
    assert "[12345] Test task" in result
    assert "Due: tomorrow" in result
    assert "Priority: P1 (Urgent)" in result
    assert "Labels: urgent, work" in result


@pytest.mark.asyncio
async def test_todoist_get_tasks_empty(mock_api_token, monkeypatch):
    """Test todoist_get_tasks with no tasks"""
    # Mock get_tasks to return empty list
    import todoist_mcp.server
    from tests.conftest import create_async_gen_mock

    monkeypatch.setattr(
        todoist_mcp.server.todoist, "get_tasks", create_async_gen_mock([])
    )

    from todoist_mcp.server import todoist_get_tasks

    result = await todoist_get_tasks()
    # Use exact match for consistent assertion style
    assert result == "No tasks found."


@pytest.mark.asyncio
async def test_todoist_get_tasks_with_label(mock_api_token, monkeypatch, mock_task):
    """Test todoist_get_tasks with label parameter"""
    from todoist_api_python.models import Task

    from tests.conftest import create_async_gen_mock

    task_obj = Task.from_dict(mock_task)
    import todoist_mcp.server

    monkeypatch.setattr(
        todoist_mcp.server.todoist, "get_tasks", create_async_gen_mock([task_obj])
    )

    from todoist_mcp.server import todoist_get_tasks

    result = await todoist_get_tasks(label="urgent")
    # Use partial match for flexible content
    assert "Found 1 task(s):" in result


@pytest.mark.asyncio
async def test_todoist_create_task_success(mock_api_token, monkeypatch, mock_task):
    """Test todoist_create_task with successful API response"""
    from todoist_api_python.models import Task

    task_obj = Task.from_dict(mock_task)

    async def mock_add_task(**kwargs):
        return task_obj

    import todoist_mcp.server

    monkeypatch.setattr(todoist_mcp.server.todoist, "add_task", mock_add_task)

    from todoist_mcp.server import todoist_create_task

    result = await todoist_create_task(content="Test task")

    # Use exact match for consistent assertion style
    assert result == "✓ Task created: Test task (ID: 12345)"


@pytest.mark.asyncio
async def test_todoist_create_task_with_all_params(
    mock_api_token, monkeypatch, mock_task
):
    """Test todoist_create_task with all parameters"""
    from todoist_api_python.models import Task

    task_obj = Task.from_dict(mock_task)

    async def mock_add_task(**kwargs):
        return task_obj

    import todoist_mcp.server

    monkeypatch.setattr(todoist_mcp.server.todoist, "add_task", mock_add_task)

    from todoist_mcp.server import todoist_create_task

    result = await todoist_create_task(
        content="Test task",
        description="Test description",
        project_id="67890",
        due_string="tomorrow",
        priority=4,
        labels=["urgent", "work"],
    )

    # Use partial matches for flexible content
    assert "✓ Task created:" in result
    assert "12345" in result


@pytest.mark.asyncio
async def test_todoist_update_task_success(mock_api_token, monkeypatch):
    """Test todoist_update_task with successful API response"""

    async def mock_update_task(**kwargs):
        return True

    import todoist_mcp.server

    monkeypatch.setattr(todoist_mcp.server.todoist, "update_task", mock_update_task)

    from todoist_mcp.server import todoist_update_task

    result = await todoist_update_task(task_id="12345", content="Updated task")

    # Use exact match for consistent assertion style
    assert result == "✓ Task 12345 updated successfully"


@pytest.mark.asyncio
async def test_todoist_update_task_multiple_fields(mock_api_token, monkeypatch):
    """Test updating multiple fields at once"""

    async def mock_update_task(**kwargs):
        return True

    import todoist_mcp.server

    monkeypatch.setattr(todoist_mcp.server.todoist, "update_task", mock_update_task)

    from todoist_mcp.server import todoist_update_task

    result = await todoist_update_task(
        task_id="12345", content="Updated", priority=3, labels=["important"]
    )

    # Use partial match for flexible content
    assert "✓ Task 12345 updated successfully" in result


@pytest.mark.asyncio
async def test_todoist_complete_task_success(mock_api_token, monkeypatch):
    """Test todoist_complete_task with successful API response"""

    async def mock_complete_task(**kwargs):
        return True

    import todoist_mcp.server

    monkeypatch.setattr(todoist_mcp.server.todoist, "complete_task", mock_complete_task)

    from todoist_mcp.server import todoist_complete_task

    result = await todoist_complete_task(task_id="12345")

    # Use exact match for consistent assertion style
    assert result == "✓ Task 12345 marked as complete"


@pytest.mark.asyncio
async def test_todoist_delete_task_success(mock_api_token, monkeypatch):
    """Test todoist_delete_task with successful API response"""

    async def mock_delete_task(**kwargs):
        return True

    import todoist_mcp.server

    monkeypatch.setattr(todoist_mcp.server.todoist, "delete_task", mock_delete_task)

    from todoist_mcp.server import todoist_delete_task

    result = await todoist_delete_task(task_id="12345")

    # Use exact match for consistent assertion style
    assert result == "✓ Task 12345 deleted"


@pytest.mark.asyncio
async def test_todoist_get_projects_success(mock_api_token, monkeypatch, mock_project):
    """Test todoist_get_projects with successful API response"""
    from todoist_api_python.models import Project

    from tests.conftest import create_async_gen_mock

    project_obj = Project.from_dict(mock_project)
    import todoist_mcp.server

    monkeypatch.setattr(
        todoist_mcp.server.todoist, "get_projects", create_async_gen_mock([project_obj])
    )

    from todoist_mcp.server import todoist_get_projects

    result = await todoist_get_projects()

    # Use partial matches for flexible content
    assert "Found 1 project(s):" in result
    assert "[67890] Test Project" in result
    assert "⭐ Favorite" in result


@pytest.mark.asyncio
async def test_todoist_get_projects_empty(mock_api_token, monkeypatch):
    """Test todoist_get_projects with no projects"""
    import todoist_mcp.server
    from tests.conftest import create_async_gen_mock

    monkeypatch.setattr(
        todoist_mcp.server.todoist, "get_projects", create_async_gen_mock([])
    )

    from todoist_mcp.server import todoist_get_projects

    result = await todoist_get_projects()
    # Use exact match for consistent assertion style
    assert result == "No projects found."


@pytest.mark.asyncio
async def test_todoist_get_projects_non_favorite(mock_api_token, monkeypatch):
    """Test todoist_get_projects with non-favorite project"""
    from todoist_api_python.models import Project

    from tests.conftest import create_async_gen_mock

    project = {
        "id": "67890",
        "name": "Regular Project",
        "color": "blue",
        "comment_count": 0,
        "order": 1,
        "is_favorite": False,
        "is_shared": False,
        "is_inbox_project": False,
        "is_team_inbox": False,
        "view_style": "list",
        "url": "https://todoist.com/showProject?id=67890",
        "parent_id": None,
        "description": "",
        "is_collapsed": False,
        "is_archived": False,
        "can_assign_tasks": False,
        "created_at": "2025-11-27T00:00:00Z",
        "updated_at": "2025-11-27T00:00:00Z",
    }
    project_obj = Project.from_dict(project)
    import todoist_mcp.server

    monkeypatch.setattr(
        todoist_mcp.server.todoist, "get_projects", create_async_gen_mock([project_obj])
    )

    from todoist_mcp.server import todoist_get_projects

    result = await todoist_get_projects()

    # Use partial matches for flexible content
    assert "[67890] Regular Project" in result
    assert "⭐ Favorite" not in result


@pytest.mark.asyncio
async def test_todoist_get_labels_success(mock_api_token, monkeypatch, mock_label):
    """Test todoist_get_labels with successful API response"""
    from todoist_api_python.models import Label

    from tests.conftest import create_async_gen_mock

    label_obj = Label.from_dict(mock_label)
    import todoist_mcp.server

    monkeypatch.setattr(
        todoist_mcp.server.todoist, "get_labels", create_async_gen_mock([label_obj])
    )

    from todoist_mcp.server import todoist_get_labels

    result = await todoist_get_labels()

    # Use partial matches for flexible content
    assert "Found 1 label(s):" in result
    assert "[11111] urgent" in result


@pytest.mark.asyncio
async def test_todoist_get_labels_empty(mock_api_token, monkeypatch):
    """Test todoist_get_labels with no labels"""
    import todoist_mcp.server
    from tests.conftest import create_async_gen_mock

    monkeypatch.setattr(
        todoist_mcp.server.todoist, "get_labels", create_async_gen_mock([])
    )

    from todoist_mcp.server import todoist_get_labels

    result = await todoist_get_labels()
    # Use exact match for consistent assertion style
    assert result == "No labels found."


@pytest.mark.asyncio
async def test_todoist_get_labels_multiple(mock_api_token, monkeypatch):
    """Test todoist_get_labels with multiple labels"""
    from todoist_api_python.models import Label

    from tests.conftest import create_async_gen_mock

    labels_data = [
        {
            "id": "11111",
            "name": "urgent",
            "color": "red",
            "order": 1,
            "is_favorite": False,
        },
        {
            "id": "22222",
            "name": "work",
            "color": "blue",
            "order": 2,
            "is_favorite": False,
        },
        {
            "id": "33333",
            "name": "personal",
            "color": "green",
            "order": 3,
            "is_favorite": False,
        },
    ]
    label_objs = [Label.from_dict(label_data) for label_data in labels_data]
    import todoist_mcp.server

    monkeypatch.setattr(
        todoist_mcp.server.todoist, "get_labels", create_async_gen_mock(label_objs)
    )

    from todoist_mcp.server import todoist_get_labels

    result = await todoist_get_labels()

    # Use partial matches for flexible content
    assert "Found 3 label(s):" in result
    assert "[11111] urgent" in result
    assert "[22222] work" in result
    assert "[33333] personal" in result


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


# Logging tests


@pytest.mark.asyncio
async def test_logger_configured_correctly(mock_api_token):
    """Test that logger is configured with correct settings"""
    from todoist_mcp.server import logger

    # Verify logger exists
    assert logger is not None
    assert logger.name == "todoist-mcp"

    # Verify logger level (should be INFO by default or from env)
    assert logger.level <= logging.INFO


@pytest.mark.asyncio
async def test_create_task_logs_info(mock_api_token, caplog):
    """Test that todoist_create_task logs at INFO level"""
    from todoist_mcp.server import todoist, todoist_create_task

    # Create a mock task object (not just dict)
    class MockTask:
        def __init__(self, task_id, content):
            self.id = task_id
            self.content = content
            self.priority = 3

    with patch.object(todoist, "add_task", return_value=MockTask("12345", "Test task")):
        with caplog.at_level(logging.INFO):
            await todoist_create_task(content="Test task")

            # Verify log messages
            assert "Tool called: todoist_create_task" in caplog.text
            assert "Test task" in caplog.text
            assert "Task created successfully" in caplog.text
            assert "12345" in caplog.text


@pytest.mark.asyncio
async def test_validation_failure_logs_warning(mock_api_token, caplog):
    """Test that validation failures log at WARNING level"""
    from todoist_mcp.server import todoist_create_task

    with caplog.at_level(logging.WARNING):
        result = await todoist_create_task(content="Test", priority=5)

        # Verify warning logged for validation failure
        assert "Validation failed" in caplog.text
        assert "Priority must be between 1 and 4" in result


@pytest.mark.asyncio
async def test_api_error_logs_error(mock_api_token, caplog):
    """Test that API errors log at ERROR level with exc_info"""
    from todoist_mcp.server import todoist, todoist_create_task

    with patch.object(
        todoist, "add_task", side_effect=Exception("API connection failed")
    ):
        with caplog.at_level(logging.ERROR):
            result = await todoist_create_task(content="Test task")

            # Verify error logged
            assert "Failed to create task" in caplog.text
            assert "API connection failed" in caplog.text
            assert "Error creating task" in result


@pytest.mark.asyncio
async def test_get_tasks_logs_count(mock_api_token, caplog):
    """Test that get_tasks logs the count of retrieved tasks"""
    from todoist_mcp.server import todoist, todoist_get_tasks

    # Create mock task objects
    class MockTask:
        def __init__(self, task_id, content):
            self.id = task_id
            self.content = content
            self.priority = 1
            self.due = None
            self.labels = []

    async def mock_generator():
        yield [
            MockTask("1", "Task 1"),
            MockTask("2", "Task 2"),
            MockTask("3", "Task 3"),
        ]

    with patch.object(todoist, "get_tasks", return_value=mock_generator()):
        with caplog.at_level(logging.INFO):
            await todoist_get_tasks()

            # Verify count logged
            assert "Retrieved 3 task(s) from Todoist" in caplog.text
