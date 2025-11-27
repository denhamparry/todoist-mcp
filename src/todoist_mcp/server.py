"""Todoist MCP Server - Complete Implementation

An MCP server that enables AI agents to manage Todoist tasks through natural
language commands.
"""

import os
from typing import List, Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from todoist_api_python.api_async import TodoistAPIAsync

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP(name="todoist-mcp")

# Initialize Todoist API client
API_TOKEN = os.getenv("TODOIST_API_TOKEN")
if not API_TOKEN:
    raise ValueError("TODOIST_API_TOKEN environment variable not set")

todoist = TodoistAPIAsync(API_TOKEN)


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
    try:
        # Get the async generator and consume it to get the list of tasks
        tasks = []
        task_generator = await todoist.get_tasks(project_id=project_id, label=label)
        async for task_batch in task_generator:
            tasks.extend(task_batch)

        if not tasks:
            return "No tasks found."

        result = f"Found {len(tasks)} task(s):\n\n"
        for task in tasks:
            result += f"- [{task.id}] {task.content}\n"
            if task.due:
                result += f"  Due: {task.due.string}\n"
            if task.priority > 1:
                # Todoist priority mapping (API uses 1-4 where higher = more urgent):
                # 1 = Normal (lowest, default - not shown)
                # 2 = Medium (P3)
                # 3 = High (P2)
                # 4 = Urgent (P1, highest)
                priority_map = {4: "P1 (Urgent)", 3: "P2 (High)", 2: "P3 (Medium)"}
                result += (
                    f"  Priority: {priority_map.get(task.priority, task.priority)}\n"
                )
            if task.labels:
                result += f"  Labels: {', '.join(task.labels)}\n"

        return result
    except Exception as e:
        return f"Error fetching tasks: {str(e)}"


@mcp.tool()
async def todoist_create_task(
    content: str,
    description: Optional[str] = None,
    project_id: Optional[str] = None,
    due_string: Optional[str] = None,
    priority: Optional[int] = None,
    labels: Optional[List[str]] = None,
) -> str:
    """Create a new task in Todoist.

    Args:
        content: Task title (required)
        description: Detailed task description
        project_id: Project ID to add task to
        due_string: Natural language due date (e.g., "tomorrow", "next Monday at 3pm")
        priority: Task priority (1=normal, 2=medium, 3=high, 4=urgent)
        labels: List of label names to apply

    Returns:
        Success message with task ID
    """
    try:
        task = await todoist.add_task(
            content=content,
            description=description,
            project_id=project_id,
            due_string=due_string,
            priority=priority,
            labels=labels,
        )
        return f"✓ Task created: {task.content} (ID: {task.id})"
    except Exception as e:
        return f"Error creating task: {str(e)}"


@mcp.tool()
async def todoist_update_task(
    task_id: str,
    content: Optional[str] = None,
    description: Optional[str] = None,
    due_string: Optional[str] = None,
    priority: Optional[int] = None,
    labels: Optional[List[str]] = None,
) -> str:
    """Update an existing task in Todoist.

    Args:
        task_id: ID of the task to update (required)
        content: New task title
        description: New task description
        due_string: New due date
        priority: New priority (1-4)
        labels: New list of label names

    Returns:
        Success message
    """
    try:
        success = await todoist.update_task(
            task_id=task_id,
            content=content,
            description=description,
            due_string=due_string,
            priority=priority,
            labels=labels,
        )
        if success:
            return f"✓ Task {task_id} updated successfully"
        else:
            return f"Failed to update task {task_id}"
    except Exception as e:
        return f"Error updating task: {str(e)}"


@mcp.tool()
async def todoist_complete_task(task_id: str) -> str:
    """Mark a task as complete in Todoist.

    Args:
        task_id: ID of the task to complete (required)

    Returns:
        Success message
    """
    try:
        success = await todoist.complete_task(task_id=task_id)
        if success:
            return f"✓ Task {task_id} marked as complete"
        else:
            return f"Failed to complete task {task_id}"
    except Exception as e:
        return f"Error completing task: {str(e)}"


@mcp.tool()
async def todoist_delete_task(task_id: str) -> str:
    """Delete a task from Todoist permanently.

    Args:
        task_id: ID of the task to delete (required)

    Returns:
        Success message
    """
    try:
        success = await todoist.delete_task(task_id=task_id)
        if success:
            return f"✓ Task {task_id} deleted"
        else:
            return f"Failed to delete task {task_id}"
    except Exception as e:
        return f"Error deleting task: {str(e)}"


@mcp.tool()
async def todoist_get_projects() -> str:
    """Get all projects from Todoist.

    Returns:
        Formatted list of projects with IDs and names
    """
    try:
        # Get the async generator and consume it to get the list of projects
        projects = []
        project_generator = await todoist.get_projects()
        async for project_batch in project_generator:
            projects.extend(project_batch)

        if not projects:
            return "No projects found."

        result = f"Found {len(projects)} project(s):\n\n"
        for project in projects:
            result += f"- [{project.id}] {project.name}\n"
            if project.is_favorite:
                result += "  ⭐ Favorite\n"

        return result
    except Exception as e:
        return f"Error fetching projects: {str(e)}"


@mcp.tool()
async def todoist_get_labels() -> str:
    """Get all labels from Todoist.

    Returns:
        Formatted list of labels with IDs and names
    """
    try:
        # Get the async generator and consume it to get the list of labels
        labels = []
        label_generator = await todoist.get_labels()
        async for label_batch in label_generator:
            labels.extend(label_batch)

        if not labels:
            return "No labels found."

        result = f"Found {len(labels)} label(s):\n\n"
        for label in labels:
            result += f"- [{label.id}] {label.name}\n"

        return result
    except Exception as e:
        return f"Error fetching labels: {str(e)}"


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
