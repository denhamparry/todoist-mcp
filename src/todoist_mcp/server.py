"""Todoist MCP Server - Complete Implementation

An MCP server that enables AI agents to manage Todoist tasks through natural
language commands.
"""

import logging
import os
import sys
from typing import List, Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from todoist_api_python.api_async import TodoistAPIAsync

# Load environment variables
load_dotenv()

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,  # MCP protocol uses stdout, so log to stderr
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("todoist-mcp")

# Initialize MCP server
mcp = FastMCP(name="todoist-mcp")

# Initialize Todoist API client
API_TOKEN = os.getenv("TODOIST_API_TOKEN")
if not API_TOKEN:
    logger.critical("TODOIST_API_TOKEN environment variable not set")
    raise ValueError("TODOIST_API_TOKEN environment variable not set")

todoist = TodoistAPIAsync(API_TOKEN)
logger.info(f"Todoist MCP Server initialized with log level: {LOG_LEVEL}")


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
            return (
                f"Error: Priority must be an integer "
                f"(received: {type(priority).__name__})"
            )
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
                return (
                    f"Error: Label at index {idx} must be a string "
                    f"(received: {type(label).__name__})"
                )
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


def is_rate_limit_error(error: Exception) -> bool:
    """Check if an exception is a rate limit error (HTTP 429).

    The todoist-api-python library raises exceptions on API errors.
    This function detects rate limit errors by checking for:
    - HTTP 429 status code in error message
    - "rate limit" keywords
    - "too many requests" keywords

    Args:
        error: Exception to check

    Returns:
        True if rate limit error, False otherwise
    """
    error_str = str(error).lower()
    return (
        "429" in str(error)
        or "rate limit" in error_str
        or "too many requests" in error_str
    )


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
    logger.info(
        f"Tool called: todoist_get_tasks - "
        f"project_id={project_id!r} label={label!r}"
    )

    # Validation
    if error := validate_project_id(project_id):
        logger.warning(f"Validation failed in todoist_get_tasks: {error}")
        return error
    if label is not None and (not label or not label.strip()):
        error_msg = "Error: Label filter cannot be empty"
        logger.warning(f"Validation failed in todoist_get_tasks: {error_msg}")
        return error_msg

    try:
        logger.debug("Fetching tasks from Todoist API")
        # Get the async generator and consume it to get the list of tasks
        tasks = []
        task_generator = await todoist.get_tasks(project_id=project_id, label=label)
        async for task_batch in task_generator:
            tasks.extend(task_batch)

        logger.info(f"Retrieved {len(tasks)} task(s) from Todoist")

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
        # Check for rate limit error and provide helpful message
        if is_rate_limit_error(e):
            logger.warning(
                f"Rate limit exceeded - tool=todoist_get_tasks "
                f"project_id={project_id!r} label={label!r}"
            )
            return (
                "Error: Todoist API rate limit exceeded. "
                "Please wait a few minutes and try again. "
                "(Standard plans: ~450 requests per 15 minutes)"
            )

        # Generic error handling
        logger.error(
            f"Failed to get tasks - project_id={project_id!r} label={label!r} "
            f"error={str(e)}",
            exc_info=True,
        )
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
    logger.info(
        f"Tool called: todoist_create_task - "
        f"content={content!r} priority={priority} due_string={due_string!r} "
        f"project_id={project_id!r} labels={labels}"
    )

    # Validation
    if error := validate_non_empty_string(content, "Content"):
        logger.warning(f"Validation failed in todoist_create_task: {error}")
        return error
    if error := validate_priority(priority):
        logger.warning(f"Validation failed in todoist_create_task: {error}")
        return error
    if error := validate_project_id(project_id):
        logger.warning(f"Validation failed in todoist_create_task: {error}")
        return error
    if error := validate_labels(labels):
        logger.warning(f"Validation failed in todoist_create_task: {error}")
        return error

    try:
        logger.debug(f"Creating task via Todoist API - content={content!r}")
        task = await todoist.add_task(
            content=content,
            description=description,
            project_id=project_id,
            due_string=due_string,
            priority=priority,
            labels=labels,
        )
        logger.info(
            f"Task created successfully - id={task.id} content={task.content!r} "
            f"priority={task.priority}"
        )
        return f"✓ Task created: {task.content} (ID: {task.id})"
    except Exception as e:
        # Check for rate limit error
        if is_rate_limit_error(e):
            logger.warning(
                f"Rate limit exceeded - tool=todoist_create_task "
                f"content={content!r}"
            )
            return (
                "Error: Todoist API rate limit exceeded. "
                "Please wait a few minutes and try again. "
                "(Standard plans: ~450 requests per 15 minutes)"
            )

        # Generic error handling
        logger.error(
            f"Failed to create task - content={content!r} error={str(e)}",
            exc_info=True,
        )
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
    logger.info(
        f"Tool called: todoist_update_task - "
        f"task_id={task_id!r} content={content!r} priority={priority} "
        f"due_string={due_string!r} labels={labels}"
    )

    # Validation
    if error := validate_task_id(task_id):
        logger.warning(f"Validation failed in todoist_update_task: {error}")
        return error
    if error := validate_priority(priority):
        logger.warning(f"Validation failed in todoist_update_task: {error}")
        return error
    if error := validate_labels(labels):
        logger.warning(f"Validation failed in todoist_update_task: {error}")
        return error

    try:
        logger.debug(f"Updating task via Todoist API - task_id={task_id!r}")
        success = await todoist.update_task(
            task_id=task_id,
            content=content,
            description=description,
            due_string=due_string,
            priority=priority,
            labels=labels,
        )
        if success:
            logger.info(f"Task updated successfully - task_id={task_id!r}")
            return f"✓ Task {task_id} updated successfully"
        else:
            logger.warning(f"Failed to update task - task_id={task_id!r}")
            return f"Failed to update task {task_id}"
    except Exception as e:
        # Check for rate limit error
        if is_rate_limit_error(e):
            logger.warning(
                f"Rate limit exceeded - tool=todoist_update_task "
                f"task_id={task_id!r}"
            )
            return (
                "Error: Todoist API rate limit exceeded. "
                "Please wait a few minutes and try again. "
                "(Standard plans: ~450 requests per 15 minutes)"
            )

        # Generic error handling
        logger.error(
            f"Failed to update task - task_id={task_id!r} error={str(e)}",
            exc_info=True,
        )
        return f"Error updating task: {str(e)}"


@mcp.tool()
async def todoist_complete_task(task_id: str) -> str:
    """Mark a task as complete in Todoist.

    Args:
        task_id: ID of the task to complete (required)

    Returns:
        Success message
    """
    logger.info(f"Tool called: todoist_complete_task - task_id={task_id!r}")

    # Validation
    if error := validate_task_id(task_id):
        logger.warning(f"Validation failed in todoist_complete_task: {error}")
        return error

    try:
        logger.debug(f"Completing task via Todoist API - task_id={task_id!r}")
        success = await todoist.complete_task(task_id=task_id)
        if success:
            logger.info(f"Task completed successfully - task_id={task_id!r}")
            return f"✓ Task {task_id} marked as complete"
        else:
            logger.warning(f"Failed to complete task - task_id={task_id!r}")
            return f"Failed to complete task {task_id}"
    except Exception as e:
        # Check for rate limit error
        if is_rate_limit_error(e):
            logger.warning(
                f"Rate limit exceeded - tool=todoist_complete_task "
                f"task_id={task_id!r}"
            )
            return (
                "Error: Todoist API rate limit exceeded. "
                "Please wait a few minutes and try again. "
                "(Standard plans: ~450 requests per 15 minutes)"
            )

        # Generic error handling
        logger.error(
            f"Failed to complete task - task_id={task_id!r} error={str(e)}",
            exc_info=True,
        )
        return f"Error completing task: {str(e)}"


@mcp.tool()
async def todoist_delete_task(task_id: str) -> str:
    """Delete a task from Todoist permanently.

    Args:
        task_id: ID of the task to delete (required)

    Returns:
        Success message
    """
    logger.info(f"Tool called: todoist_delete_task - task_id={task_id!r}")

    # Validation
    if error := validate_task_id(task_id):
        logger.warning(f"Validation failed in todoist_delete_task: {error}")
        return error

    try:
        logger.debug(f"Deleting task via Todoist API - task_id={task_id!r}")
        success = await todoist.delete_task(task_id=task_id)
        if success:
            logger.info(f"Task deleted successfully - task_id={task_id!r}")
            return f"✓ Task {task_id} deleted"
        else:
            logger.warning(f"Failed to delete task - task_id={task_id!r}")
            return f"Failed to delete task {task_id}"
    except Exception as e:
        # Check for rate limit error
        if is_rate_limit_error(e):
            logger.warning(
                f"Rate limit exceeded - tool=todoist_delete_task "
                f"task_id={task_id!r}"
            )
            return (
                "Error: Todoist API rate limit exceeded. "
                "Please wait a few minutes and try again. "
                "(Standard plans: ~450 requests per 15 minutes)"
            )

        # Generic error handling
        logger.error(
            f"Failed to delete task - task_id={task_id!r} error={str(e)}",
            exc_info=True,
        )
        return f"Error deleting task: {str(e)}"


@mcp.tool()
async def todoist_get_projects() -> str:
    """Get all projects from Todoist.

    Returns:
        Formatted list of projects with IDs and names
    """
    logger.info("Tool called: todoist_get_projects")

    try:
        logger.debug("Fetching projects from Todoist API")
        # Get the async generator and consume it to get the list of projects
        projects = []
        project_generator = await todoist.get_projects()
        async for project_batch in project_generator:
            projects.extend(project_batch)

        logger.info(f"Retrieved {len(projects)} project(s) from Todoist")

        if not projects:
            return "No projects found."

        result = f"Found {len(projects)} project(s):\n\n"
        for project in projects:
            result += f"- [{project.id}] {project.name}\n"
            if project.is_favorite:
                result += "  ⭐ Favorite\n"

        return result
    except Exception as e:
        # Check for rate limit error
        if is_rate_limit_error(e):
            logger.warning("Rate limit exceeded - tool=todoist_get_projects")
            return (
                "Error: Todoist API rate limit exceeded. "
                "Please wait a few minutes and try again. "
                "(Standard plans: ~450 requests per 15 minutes)"
            )

        # Generic error handling
        logger.error(f"Failed to get projects - error={str(e)}", exc_info=True)
        return f"Error fetching projects: {str(e)}"


@mcp.tool()
async def todoist_get_labels() -> str:
    """Get all labels from Todoist.

    Returns:
        Formatted list of labels with IDs and names
    """
    logger.info("Tool called: todoist_get_labels")

    try:
        logger.debug("Fetching labels from Todoist API")
        # Get the async generator and consume it to get the list of labels
        labels = []
        label_generator = await todoist.get_labels()
        async for label_batch in label_generator:
            labels.extend(label_batch)

        logger.info(f"Retrieved {len(labels)} label(s) from Todoist")

        if not labels:
            return "No labels found."

        result = f"Found {len(labels)} label(s):\n\n"
        for label in labels:
            result += f"- [{label.id}] {label.name}\n"

        return result
    except Exception as e:
        # Check for rate limit error
        if is_rate_limit_error(e):
            logger.warning("Rate limit exceeded - tool=todoist_get_labels")
            return (
                "Error: Todoist API rate limit exceeded. "
                "Please wait a few minutes and try again. "
                "(Standard plans: ~450 requests per 15 minutes)"
            )

        # Generic error handling
        logger.error(f"Failed to get labels - error={str(e)}", exc_info=True)
        return f"Error fetching labels: {str(e)}"


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
