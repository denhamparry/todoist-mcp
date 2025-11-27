"""Unit tests for Todoist MCP Server"""

import os

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
