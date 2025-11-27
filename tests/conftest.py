"""Pytest configuration and fixtures for Todoist MCP Server tests"""

import os

import pytest
from todoist_api_python.api_async import TodoistAPIAsync


@pytest.fixture
def mock_api_token(monkeypatch):
    """Mock API token for testing"""
    monkeypatch.setenv("TODOIST_API_TOKEN", "test_token_12345")
    return "test_token_12345"


@pytest.fixture
def todoist_client():
    """Create a Todoist API client for integration tests"""
    api_token = os.getenv("TODOIST_API_TOKEN")
    if not api_token:
        pytest.skip("TODOIST_API_TOKEN not set - skipping integration test")
    return TodoistAPIAsync(api_token)


@pytest.fixture
def test_project_id():
    """Get test project ID from environment"""
    project_id = os.getenv("TODOIST_TEST_PROJECT_ID")
    if not project_id:
        pytest.skip("TODOIST_TEST_PROJECT_ID not set - skipping integration test")
    return project_id


@pytest.fixture
def mock_task():
    """Create a mock Todoist task object"""
    return {
        "id": "12345",
        "content": "Test task",
        "description": "Test description",
        "project_id": "67890",
        "section_id": None,
        "parent_id": None,
        "order": 1,
        "due": {"string": "tomorrow", "date": "2025-11-28"},
        "priority": 4,
        "labels": ["urgent", "work"],
        "creator_id": "1",
        "created_at": "2025-11-27T00:00:00Z",
        "assignee_id": None,
        "assigner_id": None,
        "completed_at": None,
        "is_collapsed": False,
        "deadline": None,
        "duration": None,
        "updated_at": "2025-11-27T00:00:00Z",
    }


@pytest.fixture
def mock_project():
    """Create a mock Todoist project object"""
    return {
        "id": "67890",
        "name": "Test Project",
        "color": "blue",
        "comment_count": 0,
        "order": 1,
        "is_favorite": True,
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


@pytest.fixture
def mock_label():
    """Create a mock Todoist label object"""
    return {
        "id": "11111",
        "name": "urgent",
        "color": "red",
        "order": 1,
        "is_favorite": False,
    }


def create_async_gen_mock(items):
    """Helper to create async generator mock that returns a list of items"""

    async def mock_method(**kwargs):
        async def _gen():
            yield items

        return _gen()

    return mock_method
