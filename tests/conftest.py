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
