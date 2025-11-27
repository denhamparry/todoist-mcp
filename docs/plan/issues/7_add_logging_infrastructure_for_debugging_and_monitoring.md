# GitHub Issue #7: Add logging infrastructure for debugging and monitoring

**Issue:** [#7](https://github.com/denhamparry/todoist-mcp/issues/7)
**Status:** Complete
**Labels:** enhancement
**Priority:** Nice to have (Future improvement)
**Date:** 2025-01-27

## Problem Statement

The Todoist MCP server currently lacks structured logging, making it difficult to:

1. Debug issues in production
2. Monitor API call behavior and success/failure rates
3. Understand server operations and performance
4. Diagnose errors with proper context
5. Track tool usage patterns

Without logging, developers and users have limited visibility into what the server is doing, especially when problems occur in production environments.

### Current Behavior

**No logging infrastructure:**

- No log configuration in `server.py`
- Tool calls execute silently (no visibility)
- API interactions are opaque
- Errors may occur without proper context
- Debugging requires code instrumentation

**When issues occur:**

- No record of what happened
- No timestamps for events
- No context about API calls
- Difficult to reproduce problems
- Hard to identify patterns

**Example - Silent execution:**

```python
@mcp.tool()
async def todoist_create_task(...):
    try:
        task = await todoist.add_task(...)
        return f"✓ Task created: {task.content} (ID: {task.id})"
    except Exception as e:
        return f"Error creating task: {str(e)}"

```text

Issues:

- No log when tool is called
- No log of API request details
- Exception caught but not logged with context
- No way to track success/failure patterns

### Expected Behavior

**Structured logging infrastructure that:**

1. **Logs tool calls** - Record when tools are invoked and with what parameters
2. **Logs API interactions** - Track Todoist API calls and their outcomes
3. **Logs errors with context** - Full stack traces and relevant state
4. **Supports log levels** - DEBUG, INFO, WARNING, ERROR
5. **Configurable** - Environment variable for log level
6. **Production-ready** - JSON format for structured parsing
7. **Secure** - Never logs API tokens or sensitive data

**Example - With logging:**

```python
@mcp.tool()
async def todoist_create_task(...):
    logger.info("Creating task", extra={
        "content": content,
        "priority": priority,
        "has_due_date": due_string is not None
    })

    try:
        task = await todoist.add_task(...)
        logger.info("Task created successfully", extra={
            "task_id": task.id,
            "content": task.content
        })
        return f"✓ Task created: {task.content} (ID: {task.id})"
    except Exception as e:
        logger.error("Failed to create task", extra={
            "error": str(e),
            "content": content
        }, exc_info=True)
        return f"Error creating task: {str(e)}"

```text

Benefits:

- Visibility into tool usage
- Track API success/failure
- Debug issues with full context
- Monitor performance patterns
- Production-ready diagnostics

## Current State Analysis

### Server Implementation

**File:** `src/todoist_mcp/server.py`

**Current structure:**

```python
"""Todoist MCP Server - Complete Implementation"""

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

```text

**Missing:**
- No `import logging`
- No logger configuration
- No logger instance creation
- No log level configuration

**7 MCP tools that need logging:**

1. `todoist_get_tasks` (line 117) - Log retrieval, filters, result count
2. `todoist_create_task` (line 170) - Log creation, parameters, task ID
3. `todoist_update_task` (line 216) - Log updates, task ID, changed fields
4. `todoist_complete_task` (line 263) - Log completion, task ID
5. `todoist_delete_task` (line 287) - Log deletion, task ID
6. `todoist_get_projects` (line 311) - Log project listing, count
7. `todoist_get_labels` (line 339) - Log label listing, count

**Current error handling:**
- Exceptions caught and returned as strings
- No logging of exceptions
- No stack traces preserved
- Limited context in error messages

### Environment Configuration

**File:** `.env.example`

**Current contents:**

```bash
# Todoist API Token
# Get your token: https://todoist.com/help/articles/find-your-api-token-Jpzx9IIlB
TODOIST_API_TOKEN=your_api_token_here

```text

**Missing:**
- No `LOG_LEVEL` configuration
- No `LOG_FORMAT` option
- No logging documentation

### Documentation

**File:** `README.md`

**Current sections:**
- Installation
- Usage with Claude Code
- Available Tools
- Examples
- Development
- Architecture

**Missing:**
- Logging configuration section
- Environment variables reference
- Debugging guide
- Troubleshooting with logs

**File:** `CLAUDE.md`

Template file - needs project-specific updates including logging configuration.

### Dependencies

**File:** `pyproject.toml`

**Current dependencies:**

```toml
dependencies = [
    "mcp>=1.22.0",
    "todoist-api-python>=2.1.9",
    "python-dotenv>=1.0.0",
    "pydantic>=2.0.0",
]

```text

**Logging requirements:**
- Python's built-in `logging` module (no new dependency needed)
- Optional: `python-json-logger` for structured JSON logging (future enhancement)

### Testing Infrastructure

**No logging tests currently exist.**

**Need to add:**
- Tests for logger configuration
- Tests for log output at different levels
- Tests for sensitive data filtering
- Tests for error logging with context

## Solution Design

### Approach

Implement structured logging using Python's built-in `logging` module with:

1. **Minimal dependencies** - Use stdlib logging (no new dependencies)
2. **Environment-based configuration** - LOG_LEVEL env var
3. **Structured output** - Key-value pairs for machine parsing
4. **Security-first** - Filter sensitive data (API tokens)
5. **MCP-compatible** - Log to stderr (stdout reserved for MCP protocol)
6. **Production-ready** - JSON format support for future enhancement

### Implementation

**Phase 1: Logger Setup**

Add logger configuration in `server.py`:

```python
import logging
import sys

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,  # MCP protocol uses stdout, so log to stderr
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger("todoist-mcp")
logger.info(f"Todoist MCP Server starting with log level: {LOG_LEVEL}")

```text

**Phase 2: Tool Call Logging**

Add logging to each tool function:

```python
@mcp.tool()
async def todoist_create_task(...):
    logger.info(
        f"Tool called: todoist_create_task - content={content!r} "
        f"priority={priority} due_string={due_string!r}"
    )

    # Validation...

    try:
        task = await todoist.add_task(...)
        logger.info(
            f"Task created successfully - id={task.id} content={task.content!r}"
        )
        return f"✓ Task created: {task.content} (ID: {task.id})"
    except Exception as e:
        logger.error(
            f"Failed to create task - content={content!r} error={str(e)}",
            exc_info=True
        )
        return f"Error creating task: {str(e)}"

```text

**Phase 3: API Interaction Logging**

Log before/after Todoist API calls:

```python
logger.debug(f"Calling Todoist API: add_task with {len(locals())} parameters")
task = await todoist.add_task(...)
logger.debug(f"Todoist API response: task_id={task.id}")

```text

**Phase 4: Validation Error Logging**

Log validation failures:

```python
if error := validate_priority(priority):
    logger.warning(f"Validation failed: {error}")
    return error

```text

**Phase 5: Environment Configuration**

Update `.env.example`:

```bash
# Todoist API Token
# Get your token: https://todoist.com/help/articles/find-your-api-token-Jpzx9IIlB
TODOIST_API_TOKEN=your_api_token_here

# Logging Configuration
# Supported levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
# Default: INFO
LOG_LEVEL=INFO

```text

**Phase 6: Documentation**

Add logging section to README.md:

```markdown
## Logging

The server uses structured logging to help with debugging and monitoring.

### Configuration

Set the log level via environment variable:

```bash
# In .env file
LOG_LEVEL=DEBUG  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

```text

### Log Levels

- **DEBUG** - Detailed diagnostic information (API calls, parameters)
- **INFO** - General informational messages (tool calls, task operations)
- **WARNING** - Warning messages (validation failures, deprecations)
- **ERROR** - Error messages (API failures, exceptions)
- **CRITICAL** - Critical errors (server startup failures)

### Log Output

Logs are written to stderr (stdout is reserved for MCP protocol).

Example log output:

```text
2025-11-27 10:30:45 - todoist-mcp - INFO - Tool called: todoist_create_task - content='Buy groceries' priority=3
2025-11-27 10:30:46 - todoist-mcp - INFO - Task created successfully - id=12345 content='Buy groceries'

```text

### Security

The logging system never logs sensitive data:

- API tokens are filtered
- Only task IDs and content are logged (user data, not credentials)

```text

### Benefits

**For Development:**
- Faster debugging with detailed logs
- Understand execution flow
- Track down edge cases
- Monitor test behavior

**For Production:**
- Monitor API success rates
- Identify performance bottlenecks
- Diagnose user-reported issues
- Track usage patterns

**For Users:**
- Self-service troubleshooting
- Better error reports
- Visibility into server behavior
- Confidence in production deployments

### Trade-offs

**Chosen approach (stdlib logging):**

✅ No new dependencies
✅ Simple configuration
✅ Well-documented
✅ Production-ready
❌ No built-in JSON formatting (can add later)

**Alternative: python-json-logger**

✅ Structured JSON output
✅ Machine-parseable
✅ Better for log aggregation
❌ New dependency
❌ Overkill for current needs

**Alternative: Custom logger**

✅ Full control
✅ Optimized for use case
❌ Maintenance burden
❌ Reinventing the wheel

## Implementation Plan

### Step 1: Add Logger Configuration

**File:** `src/todoist_mcp/server.py`

**Changes:** Add logging imports and configuration after existing imports (after line 12):

```python
import logging
import sys

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

```text

**Testing:**

```bash
# Test with default INFO level
LOG_LEVEL=INFO uv run python -m todoist_mcp.server &
# Should see INFO log messages

# Test with DEBUG level
LOG_LEVEL=DEBUG uv run python -m todoist_mcp.server &
# Should see DEBUG and INFO messages

# Test with ERROR level
LOG_LEVEL=ERROR uv run python -m todoist_mcp.server &
# Should only see ERROR and CRITICAL messages

```text

### Step 2: Add Logging to todoist_get_tasks

**File:** `src/todoist_mcp/server.py`

**Changes:** Add logging to `todoist_get_tasks` function (update lines 117-167):

```python
@mcp.tool()
async def todoist_get_tasks(
    project_id: Optional[str] = None,
    label: Optional[str] = None,
) -> str:
    """Get tasks from Todoist with optional filtering."""
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
        tasks = []
        task_generator = await todoist.get_tasks(project_id=project_id, label=label)
        async for task_batch in task_generator:
            tasks.extend(task_batch)

        logger.info(f"Retrieved {len(tasks)} task(s) from Todoist")

        if not tasks:
            return "No tasks found."

        result = f"Found {len(tasks)} task(s):\n\n"
        # ... rest of implementation

        return result
    except Exception as e:
        logger.error(
            f"Failed to get tasks - project_id={project_id!r} label={label!r} "
            f"error={str(e)}",
            exc_info=True,
        )
        return f"Error fetching tasks: {str(e)}"

```text

**Testing:**

```bash
# Run tests with logging enabled
LOG_LEVEL=DEBUG pytest tests/test_server.py::test_todoist_get_tasks_success -v -s

# Verify logs appear in stderr
# Should see: "Tool called: todoist_get_tasks", "Retrieved N task(s)"

```text

### Step 3: Add Logging to todoist_create_task

**File:** `src/todoist_mcp/server.py`

**Changes:** Add logging to `todoist_create_task` function (update lines 170-213):

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
        logger.error(
            f"Failed to create task - content={content!r} error={str(e)}",
            exc_info=True,
        )
        return f"Error creating task: {str(e)}"

```text

**Testing:**

```bash
LOG_LEVEL=INFO pytest tests/test_server.py::test_todoist_create_task_success -v -s
# Should see: "Tool called: todoist_create_task", "Task created successfully"

```text

### Step 4: Add Logging to todoist_update_task

**File:** `src/todoist_mcp/server.py`

**Changes:** Add logging to `todoist_update_task` function (update lines 216-260):

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
        logger.error(
            f"Failed to update task - task_id={task_id!r} error={str(e)}",
            exc_info=True,
        )
        return f"Error updating task: {str(e)}"

```text

**Testing:**

```bash
LOG_LEVEL=INFO pytest tests/test_server.py::test_todoist_update_task_success -v -s

```text

### Step 5: Add Logging to todoist_complete_task and todoist_delete_task

**File:** `src/todoist_mcp/server.py`

**Changes:** Add logging to both functions (update lines 263-308):

```python
@mcp.tool()
async def todoist_complete_task(task_id: str) -> str:
    """Mark a task as complete in Todoist."""
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
        logger.error(
            f"Failed to complete task - task_id={task_id!r} error={str(e)}",
            exc_info=True,
        )
        return f"Error completing task: {str(e)}"


@mcp.tool()
async def todoist_delete_task(task_id: str) -> str:
    """Delete a task from Todoist permanently."""
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
        logger.error(
            f"Failed to delete task - task_id={task_id!r} error={str(e)}",
            exc_info=True,
        )
        return f"Error deleting task: {str(e)}"

```text

**Testing:**

```bash
LOG_LEVEL=INFO pytest tests/test_server.py::test_todoist_complete_task_success -v -s
LOG_LEVEL=INFO pytest tests/test_server.py::test_todoist_delete_task_success -v -s

```text

### Step 6: Add Logging to todoist_get_projects and todoist_get_labels

**File:** `src/todoist_mcp/server.py`

**Changes:** Add logging to both functions (update lines 311-362):

```python
@mcp.tool()
async def todoist_get_projects() -> str:
    """Get all projects from Todoist."""
    logger.info("Tool called: todoist_get_projects")

    try:
        logger.debug("Fetching projects from Todoist API")
        projects = []
        project_generator = await todoist.get_projects()
        async for project_batch in project_generator:
            projects.extend(project_batch)

        logger.info(f"Retrieved {len(projects)} project(s) from Todoist")

        if not projects:
            return "No projects found."

        result = f"Found {len(projects)} project(s):\n\n"
        # ... rest of implementation

        return result
    except Exception as e:
        logger.error(f"Failed to get projects - error={str(e)}", exc_info=True)
        return f"Error fetching projects: {str(e)}"


@mcp.tool()
async def todoist_get_labels() -> str:
    """Get all labels from Todoist."""
    logger.info("Tool called: todoist_get_labels")

    try:
        logger.debug("Fetching labels from Todoist API")
        labels = []
        label_generator = await todoist.get_labels()
        async for label_batch in label_generator:
            labels.extend(label_batch)

        logger.info(f"Retrieved {len(labels)} label(s) from Todoist")

        if not labels:
            return "No labels found."

        result = f"Found {len(labels)} label(s):\n\n"
        # ... rest of implementation

        return result
    except Exception as e:
        logger.error(f"Failed to get labels - error={str(e)}", exc_info=True)
        return f"Error fetching labels: {str(e)}"

```text

**Testing:**

```bash
LOG_LEVEL=INFO pytest tests/test_server.py::test_todoist_get_projects_success -v -s
LOG_LEVEL=INFO pytest tests/test_server.py::test_todoist_get_labels_success -v -s

```text

### Step 7: Update .env.example

**File:** `.env.example`

**Changes:** Add logging configuration:

```bash
# Todoist API Token
# Get your token: https://todoist.com/help/articles/find-your-api-token-Jpzx9IIlB
TODOIST_API_TOKEN=your_api_token_here

# Logging Configuration
# Supported levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
# Default: INFO
#
# Recommended levels:
#   - Development: DEBUG (detailed diagnostic information)
#   - Production: INFO (general informational messages)
#   - Troubleshooting: DEBUG (when diagnosing issues)
LOG_LEVEL=INFO

```text

**Testing:**

```bash
# Verify example file is valid
cat .env.example
# Should show Todoist token and LOG_LEVEL configuration

```text

### Step 8: Add Logging Documentation to README.md

**File:** `README.md`

**Changes:** Add new "Logging" section after "Usage with Claude Code" section (after line 101):

```markdown
## Logging

The server uses structured logging to help with debugging and monitoring.

### Configuration

Set the log level via environment variable in your `.env` file:

```bash
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

```text

Or when configuring the MCP server:

```json
{
  "mcpServers": {
    "todoist": {
      "command": "uv",
      "args": ["run", "todoist-mcp"],
      "env": {
        "TODOIST_API_TOKEN": "your_token_here",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}

```text

### Log Levels

- **DEBUG** - Detailed diagnostic information (API calls, parameters, internal operations)
- **INFO** - General informational messages (tool calls, successful operations, task counts)
- **WARNING** - Warning messages (validation failures, failed operations)
- **ERROR** - Error messages (API failures, exceptions with stack traces)
- **CRITICAL** - Critical errors (server startup failures, configuration errors)

### Log Output

All logs are written to **stderr** (stdout is reserved for the MCP protocol communication).

**Example log output:**

```text
2025-11-27 10:30:45 - todoist-mcp - INFO - Todoist MCP Server initialized with log level: INFO
2025-11-27 10:30:50 - todoist-mcp - INFO - Tool called: todoist_create_task - content='Buy groceries' priority=3
2025-11-27 10:30:51 - todoist-mcp - INFO - Task created successfully - id=12345 content='Buy groceries' priority=3
2025-11-27 10:31:00 - todoist-mcp - INFO - Tool called: todoist_get_tasks - project_id=None label=None
2025-11-27 10:31:01 - todoist-mcp - INFO - Retrieved 15 task(s) from Todoist

```text

### Debugging

When troubleshooting issues, set `LOG_LEVEL=DEBUG` for detailed diagnostic information:

```bash
# In .env file
LOG_LEVEL=DEBUG

```text

This will show:

- All tool calls with full parameters
- Todoist API interactions
- Validation checks
- Internal operations

### Security

The logging system is designed with security in mind:

- **API tokens are never logged** - Token values are filtered from all log output
- **Only necessary data is logged** - Task IDs, content, and metadata (not sensitive credentials)
- **Exceptions include context** - Error logs include stack traces for debugging without exposing secrets

### Viewing Logs

Logs are output to stderr. To view them:

**When running directly:**

```bash
uv run python -m todoist_mcp.server
# Logs appear in terminal

```text

**When using with Claude Code:**
- Logs are captured by the Claude Code MCP framework
- Check your MCP server logs in the Claude Code interface
- Or redirect stderr to a file in your MCP configuration

```text

**Testing:**

```bash
# Verify README has proper formatting
grep -A 10 "## Logging" README.md
# Should show the new Logging section

```text

### Step 9: Update CLAUDE.md with Logging Information

**File:** `CLAUDE.md`

**Changes:** Add logging section to Quick Commands or create new Debugging section:

```markdown
## Quick Commands

```bash
# Build: N/A (Python project)
# Test: pytest
# Test with coverage: pytest --cov=src/todoist_mcp --cov-report=html
# Lint: pre-commit run --all-files
# Type Check: mypy src/
# Run server: uv run python -m todoist_mcp.server
# Run with debug logging: LOG_LEVEL=DEBUG uv run python -m todoist_mcp.server

```text

## Debugging

### Logging

The server uses Python's built-in logging module with the following configuration:

- **Default log level:** INFO
- **Log output:** stderr (stdout reserved for MCP protocol)
- **Configuration:** Set `LOG_LEVEL` environment variable

**Available log levels:**
- DEBUG - Detailed diagnostic information
- INFO - General informational messages (default)
- WARNING - Warning messages
- ERROR - Error messages with stack traces
- CRITICAL - Critical errors

**Enable debug logging:**

```bash
# In .env file
LOG_LEVEL=DEBUG

# Or when running directly
LOG_LEVEL=DEBUG uv run python -m todoist_mcp.server

```text

**Log format:**

```text
YYYY-MM-DD HH:MM:SS - logger-name - LEVEL - message

```text

### Common Debugging Scenarios

**Issue: Tool not working as expected**
1. Set `LOG_LEVEL=DEBUG`
2. Run the tool
3. Check logs for tool call parameters and API responses

**Issue: API errors**
1. Check ERROR level logs for exception details
2. Look for stack traces (exc_info=True)
3. Verify API token is valid

**Issue: Validation failures**
1. Check WARNING level logs for validation error messages
2. Verify parameter values in log output

```text

**Testing:**

```bash
# Verify CLAUDE.md updated
grep -A 5 "Debugging" CLAUDE.md
# Should show debugging section with logging info

```text

### Step 10: Add Logging Tests

**File:** `tests/test_server.py`

**Changes:** Add new test section for logging verification:

```python
import logging
from unittest.mock import patch


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
async def test_create_task_logs_info(mock_api_token, mock_task, caplog):
    """Test that todoist_create_task logs at INFO level"""
    from todoist_mcp.server import todoist_create_task, todoist

    with patch.object(todoist, "add_task", return_value=mock_task("12345")):
        with caplog.at_level(logging.INFO):
            result = await todoist_create_task(content="Test task")

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
    from todoist_mcp.server import todoist_create_task, todoist

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
async def test_get_tasks_logs_count(mock_api_token, mock_task, caplog):
    """Test that get_tasks logs the count of retrieved tasks"""
    from todoist_mcp.server import todoist_get_tasks, todoist

    async def mock_generator():
        yield [mock_task("1"), mock_task("2"), mock_task("3")]

    with patch.object(todoist, "get_tasks", return_value=mock_generator()):
        with caplog.at_level(logging.INFO):
            result = await todoist_get_tasks()

            # Verify count logged
            assert "Retrieved 3 task(s) from Todoist" in caplog.text

```text

**Testing:**

```bash
# Run logging tests
pytest tests/test_server.py -k "test_logger or logs" -v

# Run all tests to ensure no regressions
pytest tests/test_server.py -v

# Check coverage includes logging code
pytest tests/test_server.py --cov=src/todoist_mcp --cov-report=term-missing

```text

### Step 11: Run Full Test Suite

**Commands:**

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/todoist_mcp --cov-report=html --cov-report=term-missing

# Verify coverage >80%
pytest tests/ --cov=src/todoist_mcp --cov-fail-under=80

```text

**Expected results:**
- All existing tests pass (~25 tests)
- All new logging tests pass (~5 tests)
- Total: ~30 tests passing
- Coverage remains >80%

### Step 12: Manual Testing with Different Log Levels

**Test scenarios:**

```bash
# Test 1: DEBUG level
LOG_LEVEL=DEBUG uv run python -m todoist_mcp.server
# Expected: See DEBUG, INFO, WARNING, ERROR logs
# Should see: "Fetching tasks from Todoist API", "Creating task via Todoist API"

# Test 2: INFO level (default)
LOG_LEVEL=INFO uv run python -m todoist_mcp.server
# Expected: See INFO, WARNING, ERROR logs (no DEBUG)
# Should see: "Tool called", "Task created successfully"
# Should NOT see: "Fetching tasks from Todoist API"

# Test 3: WARNING level
LOG_LEVEL=WARNING uv run python -m todoist_mcp.server
# Expected: See only WARNING and ERROR logs
# Should see: Validation failures
# Should NOT see: "Tool called", "Task created"

# Test 4: ERROR level
LOG_LEVEL=ERROR uv run python -m todoist_mcp.server
# Expected: See only ERROR logs
# Should see: Exception stack traces
# Should NOT see: Info or warning messages

# Test 5: Invalid log level (should default to INFO)
LOG_LEVEL=INVALID uv run python -m todoist_mcp.server
# Expected: Defaults to INFO level
# Should see: INFO level messages

```text

## Testing Strategy

### Unit Testing

**Logger Configuration Tests:**
- Verify logger instance created correctly
- Verify logger name is "todoist-mcp"
- Verify log level respects LOG_LEVEL env var
- Verify logs go to stderr (not stdout)

**Log Output Tests:**
- Verify INFO logs for tool calls
- Verify DEBUG logs for API calls
- Verify WARNING logs for validation failures
- Verify ERROR logs for exceptions with exc_info=True

### Integration Testing

**End-to-end logging flow:**
1. Call tool → Verify "Tool called" log
2. Validation passes → No warning log
3. API succeeds → Verify "successfully" log
4. API fails → Verify ERROR log with exception

**Log level behavior:**
- DEBUG: All messages logged
- INFO: Tool calls and success messages
- WARNING: Only validation and failures
- ERROR: Only exception errors

### Manual Testing

**Test with MCP inspector:**

```bash
# Run server with debug logging
LOG_LEVEL=DEBUG npx @modelcontextprotocol/inspector uv run python -m todoist_mcp.server

# Call tools and observe logs in stderr
# Verify no logs appear in stdout (would break MCP protocol)

```text

**Test in production configuration:**

```bash
# Test with Claude Code MCP settings
# Verify logs appear in Claude Code MCP server logs
# Verify tools still work correctly with logging enabled

```text

### Security Testing

**Verify sensitive data filtering:**
- API token never appears in logs
- Only task IDs and content logged (public data)
- Exception messages don't expose credentials

**Test cases:**

```python
# Should NOT log token
logger.info(f"Initializing with token: {API_TOKEN}")  # BAD - don't do this
logger.info("Todoist MCP Server initialized")  # GOOD

# Should log task data (not sensitive)
logger.info(f"Task created: id={task.id} content={task.content}")  # GOOD

```text

## Success Criteria

- [ ] Logger configured in server.py with LOG_LEVEL env var support
- [ ] Logger uses stderr (not stdout)
- [ ] Logger initialized message on startup
- [ ] Logging added to all 7 MCP tool functions
- [ ] INFO logs for tool calls with key parameters
- [ ] DEBUG logs for API interactions
- [ ] WARNING logs for validation failures
- [ ] ERROR logs for exceptions with exc_info=True
- [ ] Success/failure logging for all operations
- [ ] .env.example updated with LOG_LEVEL configuration
- [ ] README.md updated with Logging section
- [ ] CLAUDE.md updated with debugging information
- [ ] Tests for logger configuration
- [ ] Tests for log output at different levels
- [ ] Tests for validation failure logging
- [ ] Tests for error logging with exceptions
- [ ] All existing tests still pass
- [ ] Manual testing with all log levels (DEBUG, INFO, WARNING, ERROR)
- [ ] No sensitive data (API tokens) in logs
- [ ] Code coverage remains >80%
- [ ] Documentation complete and accurate

## Files Modified

1. **`src/todoist_mcp/server.py`**
   - Add logging imports (logging, sys)
   - Add LOG_LEVEL configuration from env var
   - Configure logging.basicConfig (stderr, format, level)
   - Create logger instance
   - Add logging to 7 MCP tool functions
   - Log tool calls, validation, API interactions, errors

2. **`.env.example`**
   - Add LOG_LEVEL configuration with documentation
   - Include recommended levels for different scenarios

3. **`README.md`**
   - Add "Logging" section after "Usage with Claude Code"
   - Document log levels and their use cases
   - Show example log output
   - Explain security considerations
   - Show how to enable debug logging

4. **`CLAUDE.md`**
   - Add logging to Quick Commands
   - Add Debugging section with logging information
   - Document common debugging scenarios

5. **`tests/test_server.py`**
   - Add logging configuration tests
   - Add log output verification tests
   - Add tests for different log levels
   - Add tests for validation/error logging

## Related Issues and Tasks

### Depends On

None - This is an independent enhancement.

### Blocks

None - Nice to have feature.

### Related

- **Future enhancement:** Add structured JSON logging for production
  - Use `python-json-logger` package
  - Machine-parseable log format
  - Better for log aggregation systems

- **Future enhancement:** Add log filtering/sampling
  - Sample DEBUG logs in production (reduce volume)
  - Filter out noisy logs
  - Configurable log filters

- **Future enhancement:** Add metrics/observability
  - Tool call counts
  - API success/failure rates
  - Performance metrics (latency)
  - Integration with monitoring systems

### Enables

- Better debugging and troubleshooting
- Production monitoring and observability
- User self-service diagnostics
- Performance analysis
- Usage pattern tracking
- Foundation for future observability enhancements

## References

- [GitHub Issue #7](https://github.com/denhamparry/todoist-mcp/issues/7)
- [Python logging documentation](https://docs.python.org/3/library/logging.html)
- [Python logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [MCP Protocol Specification](https://modelcontextprotocol.io/) - stdout reserved for protocol
- [Todoist API Documentation](https://developer.todoist.com/rest/v2/)
- Current server implementation: `src/todoist_mcp/server.py:1-372`

## Notes

### Key Insights

1. **stderr vs stdout** - Critical for MCP compatibility (stdout reserved for protocol)
2. **Environment-based config** - LOG_LEVEL env var allows runtime configuration
3. **Structured logging** - Key-value format enables future JSON logging migration
4. **Security first** - Never log API tokens or credentials
5. **Fail-safe defaults** - Default to INFO level if LOG_LEVEL invalid
6. **Context in errors** - exc_info=True preserves stack traces for debugging
7. **Validation logging** - Log validation failures at WARNING level

### Alternative Approaches Considered

1. **python-json-logger** - Structured JSON output ❌
   - Pros: Machine-parseable, better for aggregation
   - Cons: New dependency, overkill for current needs
   - Decision: Use stdlib logging now, migrate later if needed

2. **Custom logger class** - Full control over behavior ❌
   - Pros: Complete customization
   - Cons: Maintenance burden, reinventing wheel
   - Decision: Stdlib logging is sufficient

3. **Log to file** - Persistent log storage ❌
   - Pros: Historical record, easier debugging
   - Cons: File management, rotation, permissions
   - Decision: Use stderr, let runtime handle persistence

4. **Stdlib logging (chosen)** - Simple, effective, no dependencies ✅
   - Pros: No dependencies, well-documented, production-ready
   - Cons: No JSON format (can add later)
   - Decision: Best balance of simplicity and functionality

### Best Practices

**Log levels:**
- DEBUG: Diagnostic details (API calls, internal state)
- INFO: Important events (tool calls, success operations)
- WARNING: Recoverable issues (validation failures)
- ERROR: Exceptions and failures (with stack traces)
- CRITICAL: Unrecoverable errors (server startup failures)

**Log messages:**
- Use f-strings for formatting
- Include key identifiers (task_id, content, etc.)
- Use repr() for strings to see quotes/whitespace
- Keep messages concise but informative
- Use consistent format across similar operations

**Security:**
- Never log API tokens
- Never log user passwords/credentials
- Log task IDs and content (not sensitive)
- Use exc_info=True for exceptions (provides context)

**Performance:**
- Logging is fast, but DEBUG can be verbose
- Use INFO or WARNING in production
- DEBUG only for troubleshooting
- Avoid excessive logging in tight loops

### Future Enhancements

**Phase 2: Structured JSON Logging**
- Add `python-json-logger` dependency
- Configure JSON formatter
- Enable machine-parseable logs
- Better integration with log aggregation

**Phase 3: Log Sampling**
- Sample DEBUG logs in production (e.g., 1% of calls)
- Reduce log volume while maintaining visibility
- Configurable sampling rate

**Phase 4: Metrics and Observability**
- Track tool call counts
- Measure API latency
- Monitor success/failure rates
- Integration with monitoring systems (Prometheus, Datadog)

**Phase 5: Advanced Features**
- Log correlation IDs (track requests across tools)
- Log filtering based on patterns
- Dynamic log level changes (without restart)
- Log rotation and archival
