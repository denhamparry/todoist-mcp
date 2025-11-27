"""Integration tests for Todoist MCP Server

These tests require a real Todoist API token and will make actual API calls.
Set TODOIST_API_TOKEN and optionally TODOIST_TEST_PROJECT_ID to run these tests.

Run with: pytest tests/test_integration.py -m integration
"""

import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_tasks_with_real_api(todoist_client):
    """Test getting tasks with real Todoist API"""
    tasks = await todoist_client.get_tasks()
    assert isinstance(tasks, list)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_projects_with_real_api(todoist_client):
    """Test getting projects with real Todoist API"""
    projects = await todoist_client.get_projects()
    assert isinstance(projects, list)
    assert len(projects) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_labels_with_real_api(todoist_client):
    """Test getting labels with real Todoist API"""
    labels = await todoist_client.get_labels()
    assert isinstance(labels, list)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_and_delete_task_workflow(todoist_client):
    """Test complete task creation and deletion workflow"""
    # Create task
    task = await todoist_client.add_task(
        content="Test task from MCP server pytest",
        description="This is a test task",
        priority=2,
    )

    assert task.id
    assert task.content == "Test task from MCP server pytest"
    assert task.priority == 2

    # Clean up - delete the task
    success = await todoist_client.delete_task(task_id=task.id)
    assert success


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_update_and_delete_task(todoist_client):
    """Test create, update, and delete task workflow"""
    # Create task
    task = await todoist_client.add_task(content="Original task title", priority=1)
    task_id = task.id

    try:
        # Update task
        success = await todoist_client.update_task(
            task_id=task_id, content="Updated task title", priority=3
        )
        assert success

        # Verify update
        updated_task = await todoist_client.get_task(task_id=task_id)
        assert updated_task.content == "Updated task title"
        assert updated_task.priority == 3

    finally:
        # Clean up
        await todoist_client.delete_task(task_id=task_id)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_complete_and_delete_task(todoist_client):
    """Test create, complete, and delete task workflow"""
    # Create task
    task = await todoist_client.add_task(content="Task to complete")
    task_id = task.id

    try:
        # Complete task
        success = await todoist_client.close_task(task_id=task_id)
        assert success

    finally:
        # Clean up - delete completed task
        await todoist_client.delete_task(task_id=task_id)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_task_with_due_date(todoist_client):
    """Test creating task with natural language due date"""
    task = await todoist_client.add_task(
        content="Task with due date", due_string="tomorrow"
    )

    try:
        assert task.id
        assert task.due is not None
        assert task.due.string == "tomorrow"

    finally:
        # Clean up
        await todoist_client.delete_task(task_id=task.id)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_task_in_specific_project(todoist_client, test_project_id):
    """Test creating task in specific project"""
    task = await todoist_client.add_task(
        content="Task in specific project", project_id=test_project_id
    )

    try:
        assert task.id
        assert task.project_id == test_project_id

    finally:
        # Clean up
        await todoist_client.delete_task(task_id=task.id)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_filter_tasks_by_project(todoist_client, test_project_id):
    """Test filtering tasks by project"""
    # Create test task in project
    task = await todoist_client.add_task(
        content="Test filter task", project_id=test_project_id
    )

    try:
        # Get tasks for project
        tasks = await todoist_client.get_tasks(project_id=test_project_id)
        task_ids = [t.id for t in tasks]

        assert task.id in task_ids

    finally:
        # Clean up
        await todoist_client.delete_task(task_id=task.id)
