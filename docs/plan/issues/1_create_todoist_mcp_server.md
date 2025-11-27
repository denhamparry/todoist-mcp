# GitHub Issue #1: Create Todoist MCP Server

**Issue:** [#1](https://github.com/denhamparry/todoist-mcp/issues/1)
**Status:** Open
**Date:** 2025-11-27
**Labels:** documentation, enhancement, mcp-server, integration

## Problem Statement

Create an MCP (Model Context Protocol) server that enables AI agents to interact with and manage tasks within Todoist through natural language commands.

### Current Behavior

- No integration exists between AI agents and Todoist
- Users cannot manage Todoist tasks through AI assistants
- Manual task management required

### Expected Behavior

- AI agents can create, read, update, and delete Todoist tasks
- Natural language commands translate to Todoist API operations
- Seamless integration between Claude Code and Todoist task management
- Support for projects, labels, priorities, and due dates

## Current State Analysis

### Repository Structure

This is a new project created from a GitHub template repository for Claude Code projects. Current structure:

- `.claude/commands/` - Custom slash commands (setup, review, tdd-check, precommit)
- `.github/` - Issue templates, PR templates, workflows, dependabot
- `docs/` - Setup documentation and planning documents
- No source code yet - clean slate for implementation

### Technology Stack Decision Needed

Based on MCP ecosystem research:

- **Python** - Official SDK available, excellent for rapid development
- **TypeScript** - Official SDK available, strong typing benefits
- **Go** - No official SDK, would require manual JSON-RPC implementation
- **Recommendation:** Python or TypeScript (both have official SDKs)

### MCP Protocol Requirements

- Implement JSON-RPC 2.0 message protocol
- Support stdio or HTTP transport (stdio recommended for local use)
- Define tools/resources/prompts following MCP specification
- Handle authentication securely (API tokens)

### Todoist API Integration

- REST API v2: <https://developer.todoist.com/rest/v2/>
- Base URL: `https://api.todoist.com/rest/v2/`
- Authentication: Bearer token (personal or OAuth)
- Note: REST API v1 was sunset in November 2022. Use v2 for all new development.
- Official Python SDK: `todoist-api-python` (recommended over manual HTTP calls)
- Main endpoints needed:
  - Tasks: GET, POST, POST (update), DELETE `/rest/v2/tasks`
  - Projects: GET `/rest/v2/projects`
  - Labels: GET `/rest/v2/labels`
  - Comments: GET, POST `/rest/v2/comments`

## Solution Design

### Approach

Build a Python-based MCP server using the official MCP SDK that exposes Todoist task management capabilities as MCP tools. Python chosen for:

1. Official MCP SDK support (`mcp` package on PyPI)
2. Official Todoist API Python SDK (`todoist-api-python`)
3. Rapid development and iteration
4. Strong community support
5. Easy testing with pytest
6. Excellent async/await support for concurrent operations

### Architecture

```text
┌─────────────────┐
│   Claude Code   │
│   (MCP Client)  │
└────────┬────────┘
         │
         │ JSON-RPC 2.0 over stdio
         │
┌────────▼────────┐
│   MCP Server    │
│   (Python)      │
│                 │
│  ┌───────────┐  │
│  │  Tools    │  │
│  │  - create │  │
│  │  - list   │  │
│  │  - update │  │
│  │  - delete │  │
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │ Todoist   │  │
│  │ API SDK   │  │
│  └───────────┘  │
└────────┬────────┘
         │
         │ HTTPS REST API v2
         │
┌────────▼────────┐
│  Todoist API    │
│  (REST v2)      │
└─────────────────┘
```

### MCP Tools to Implement

#### 1. `todoist_get_tasks`

**Description:** Retrieve tasks with optional filtering
**Parameters:**

- `project_id` (optional): Filter by project
- `label` (optional): Filter by label
- `filter` (optional): Todoist filter query

**Returns:** List of tasks with id, content, description, due date, priority, labels

#### 2. `todoist_create_task`

**Description:** Create a new task
**Parameters:**

- `content` (required): Task title
- `description` (optional): Task description
- `project_id` (optional): Project ID
- `due_string` (optional): Natural language due date (e.g., "tomorrow", "next Monday")
- `priority` (optional): 1-4 (1=normal, 4=urgent)
- `labels` (optional): List of label names

**Returns:** Created task object

#### 3. `todoist_update_task`

**Description:** Update an existing task
**Parameters:**

- `task_id` (required): Task ID to update
- `content` (optional): New task title
- `description` (optional): New description
- `due_string` (optional): New due date
- `priority` (optional): New priority

**Returns:** Updated task object

#### 4. `todoist_complete_task`

**Description:** Mark a task as complete
**Parameters:**

- `task_id` (required): Task ID to complete

**Returns:** Success confirmation

#### 5. `todoist_delete_task`

**Description:** Delete a task
**Parameters:**

- `task_id` (required): Task ID to delete

**Returns:** Success confirmation

#### 6. `todoist_get_projects`

**Description:** List all projects
**Returns:** List of projects with id, name, color

#### 7. `todoist_get_labels`

**Description:** List all labels
**Returns:** List of labels with id, name, color

### Configuration

Store API token in environment variable or configuration file:

```bash
# .env (not committed to git)
TODOIST_API_TOKEN=your_api_token_here
```

**Security:**

- Never commit API tokens to version control
- Use `.env` file with `.gitignore` entry
- Provide `.env.example` with template
- Document token acquisition in README

### Error Handling

- Validate API token before operations
- Handle HTTP errors (401, 403, 404, 429, 500)
- Provide clear error messages to AI agent
- Implement rate limiting respect (429 responses)
- Timeout handling for API requests

### Testing Strategy

1. **Unit Tests:** Mock Todoist API responses
2. **Integration Tests:** Test against real Todoist account (test project)
3. **TDD Approach:** Write tests before implementation
4. **Test Coverage:** Aim for >80%

## Implementation Plan

### Step 1: Project Setup and Dependencies

**Files:**

- `pyproject.toml` - Python project configuration (recommended)
- `.env.example` - Environment template
- `.gitignore` - Update to ignore .env, **pycache**, .venv, etc.
- `src/todoist_mcp/__init__.py` - Package initialization

**Changes:**

1. Initialize Python project structure (choose one approach):

   **Option A: Using `uv` (Recommended - Modern, Fast)**

   ```bash
   # Install uv if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Initialize project
   uv init todoist-mcp
   cd todoist-mcp

   # Add dependencies
   uv add mcp todoist-api-python python-dotenv pydantic
   uv add --dev pytest pytest-asyncio pytest-cov black isort flake8 mypy
   ```

   **Option B: Using `pip` (Traditional)**

   ```bash
   # Create project structure
   mkdir -p src/todoist_mcp tests
   touch src/todoist_mcp/__init__.py

   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install dependencies (after creating pyproject.toml)
   pip install -e ".[dev]"
   ```

2. Create `pyproject.toml` with dependencies:

   ```toml
   [build-system]
   requires = ["setuptools>=68.0.0", "wheel"]
   build-backend = "setuptools.build_meta"

   [project]
   name = "todoist-mcp"
   version = "0.1.0"
   description = "MCP server for Todoist task management"
   requires-python = ">=3.10"
   dependencies = [
       "mcp>=1.22.0",
       "todoist-api-python>=2.1.9",
       "python-dotenv>=1.0.0",
       "pydantic>=2.0.0",
   ]

   [project.optional-dependencies]
   dev = [
       "pytest>=8.0.0",
       "pytest-asyncio>=0.23.0",
       "pytest-cov>=4.1.0",
       "pytest-httpx>=0.30.0",
       "black>=24.0.0",
       "isort>=5.13.0",
       "flake8>=7.0.0",
       "mypy>=1.11.0",
   ]

   [project.scripts]
   todoist-mcp = "todoist_mcp.server:main"

   [tool.pytest.ini_options]
   testpaths = ["tests"]
   python_files = "test_*.py"
   asyncio_mode = "auto"
   addopts = "--cov=src/todoist_mcp --cov-report=term-missing --cov-fail-under=80"

   [tool.black]
   line-length = 88
   target-version = ["py310"]

   [tool.isort]
   profile = "black"
   ```

3. Update `.gitignore` for Python:

   ```text
   # Existing entries
   .env

   # Python
   __pycache__/
   *.py[cod]
   *$py.class
   *.so
   .Python
   build/
   develop-eggs/
   dist/
   downloads/
   eggs/
   .eggs/
   lib/
   lib64/
   parts/
   sdist/
   var/
   wheels/
   *.egg-info/
   .installed.cfg
   *.egg

   # Virtual environments
   .venv/
   venv/
   ENV/
   env/

   # Testing
   .pytest_cache/
   .coverage
   htmlcov/

   # IDE
   .vscode/
   .idea/
   *.swp
   *.swo
   *~
   ```

**Key Dependencies:**

- `mcp>=1.22.0` - Official MCP SDK (latest with 2025-06-18 spec support)
- `todoist-api-python>=2.1.9` - Official Todoist Python SDK (async support included)
- `python-dotenv>=1.0.0` - Environment variable management
- `pydantic>=2.0.0` - Data validation and settings management
- `pytest>=8.0.0` - Testing framework
- `pytest-asyncio>=0.23.0` - Async test support
- `pytest-httpx>=0.30.0` - HTTP mocking for tests

**Testing:**

```bash
# Using uv
uv run python -c "import mcp; from todoist_api_python.api import TodoistAPI; import dotenv; print('All imports successful')"

# Using pip
python -c "import mcp; from todoist_api_python.api import TodoistAPI; import dotenv; print('All imports successful')"

# Verify pytest works
pytest --version
```

### Step 2: Create MCP Server Foundation

**File:** `src/todoist_mcp/server.py`

**Changes:**

1. Create MCP server using modern FastMCP API (simpler than low-level Server class)
2. Initialize with name and version
3. Configure Todoist API client
4. Load API token from environment
5. Set up error handling

**Code Example (Recommended - Using FastMCP):**

```python
"""Todoist MCP Server

An MCP server that enables AI agents to manage Todoist tasks.
"""
import os
from typing import Optional
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from todoist_api_python.api_async import TodoistAPIAsync

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP(name="todoist-mcp", version="0.1.0")

# Initialize Todoist API client
API_TOKEN = os.getenv("TODOIST_API_TOKEN")
if not API_TOKEN:
    raise ValueError("TODOIST_API_TOKEN environment variable not set")

todoist = TodoistAPIAsync(API_TOKEN)


# Tool implementations will be added in Step 4
@mcp.tool()
async def todoist_get_tasks(
    project_id: Optional[str] = None,
    filter: Optional[str] = None
) -> str:
    """Get tasks from Todoist with optional filtering.

    Args:
        project_id: Filter tasks by project ID
        filter: Todoist filter query (e.g., "today", "p1")

    Returns:
        Formatted list of tasks
    """
    try:
        tasks = await todoist.get_tasks(project_id=project_id, filter=filter)

        if not tasks:
            return "No tasks found."

        result = f"Found {len(tasks)} task(s):\n\n"
        for task in tasks:
            result += f"- [{task.id}] {task.content}\n"
            if task.due:
                result += f"  Due: {task.due.string}\n"
            if task.priority > 1:
                result += f"  Priority: {task.priority}\n"

        return result
    except Exception as e:
        return f"Error fetching tasks: {str(e)}"


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
```

**Alternative (Low-Level Server API):**

```python
"""Low-level Server API alternative (more control, more complex)"""
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import os
from dotenv import load_dotenv
from todoist_api_python.api_async import TodoistAPIAsync

load_dotenv()

app = Server("todoist-mcp")
todoist = TodoistAPIAsync(os.getenv("TODOIST_API_TOKEN"))


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="todoist_get_tasks",
            description="Get tasks from Todoist",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "Project ID"},
                    "filter": {"type": "string", "description": "Filter query"}
                }
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    if name == "todoist_get_tasks":
        tasks = await todoist.get_tasks(
            project_id=arguments.get("project_id"),
            filter=arguments.get("filter")
        )
        content = f"Found {len(tasks)} tasks"
        return [TextContent(type="text", text=content)]


def main():
    """Run the server"""
    stdio_server(app)


if __name__ == "__main__":
    main()
```

**Recommendation:** Use FastMCP unless you need low-level control. FastMCP automatically handles:

- Tool registration and schema generation
- Type hint parsing for parameters
- Error responses
- Stdio transport setup

**Testing:**

```bash
# Using uv
uv run python -m todoist_mcp.server

# Using pip (with activated venv)
python -m todoist_mcp.server

# Test with MCP inspector (if available)
npx @modelcontextprotocol/inspector python -m todoist_mcp.server

# Verify server responds (manual JSON-RPC test)
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python -m todoist_mcp.server
```

### Step 3: Using the Official Todoist SDK

**Note:** This step is simplified because we're using the official `todoist-api-python` SDK instead of building a custom HTTP client.

**Benefits of Official SDK:**

- ✅ Maintained by Todoist team
- ✅ Type hints and IDE support
- ✅ Built-in error handling
- ✅ Automatic authentication
- ✅ Async support included (`TodoistAPIAsync`)
- ✅ Well-tested and stable

**Key Methods Available:**

```python
from todoist_api_python.api_async import TodoistAPIAsync

# Initialize
todoist = TodoistAPIAsync("your_api_token")

# Tasks
tasks = await todoist.get_tasks(project_id="...", filter="today")
task = await todoist.add_task(content="New task", due_string="tomorrow", priority=4)
task = await todoist.get_task(task_id="...")
success = await todoist.update_task(task_id="...", content="Updated")
success = await todoist.close_task(task_id="...")  # Mark complete
success = await todoist.delete_task(task_id="...")

# Projects
projects = await todoist.get_projects()
project = await todoist.get_project(project_id="...")

# Labels
labels = await todoist.get_labels()

# Comments
comments = await todoist.get_comments(task_id="...")
comment = await todoist.add_comment(task_id="...", content="Comment text")
```

**Error Handling:**

The SDK raises exceptions for errors:

```python
from todoist_api_python.api_async import TodoistAPIAsync
from todoist_api_python.http_requests import HttpxClient

try:
    task = await todoist.get_task("invalid_id")
except Exception as e:
    # Handle API errors
    error_msg = f"Todoist API error: {str(e)}"
```

**Testing with Official SDK:**

```python
# tests/test_todoist_integration.py
import pytest
from todoist_api_python.api_async import TodoistAPIAsync

@pytest.mark.asyncio
async def test_get_tasks_with_official_sdk():
    """Test using official SDK (requires real API token for integration tests)"""
    import os
    api_token = os.getenv("TODOIST_API_TOKEN")

    if not api_token:
        pytest.skip("TODOIST_API_TOKEN not set")

    todoist = TodoistAPIAsync(api_token)
    tasks = await todoist.get_tasks()

    assert isinstance(tasks, list)

@pytest.mark.asyncio
async def test_create_and_delete_task():
    """Full lifecycle test"""
    import os
    api_token = os.getenv("TODOIST_API_TOKEN")

    if not api_token:
        pytest.skip("TODOIST_API_TOKEN not set")

    todoist = TodoistAPIAsync(api_token)

    # Create
    task = await todoist.add_task(content="Test task from pytest")
    assert task.content == "Test task from pytest"

    # Cleanup
    await todoist.delete_task(task_id=task.id)
```

**Documentation:**

- API Reference: <https://doist.github.io/todoist-api-python/>
- GitHub: <https://github.com/Doist/todoist-api-python>
- REST API Docs: <https://developer.todoist.com/rest/v2/>

### Step 4: Implement MCP Tool Handlers

**File:** `src/todoist_mcp/server.py` (add to existing file)

**Changes:**

1. Implement tool functions using FastMCP decorators
2. Use official Todoist SDK methods
3. Add comprehensive error handling
4. Format responses for readability
5. Document all parameters clearly

**Note:** With FastMCP, we add tools directly in `server.py` using `@mcp.tool()` decorators. No separate tools.py file needed.

**Complete Implementation:**

```python
"""Todoist MCP Server - Complete Implementation"""
import os
from typing import Optional, List
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from todoist_api_python.api_async import TodoistAPIAsync

load_dotenv()

# Initialize
mcp = FastMCP(name="todoist-mcp", version="0.1.0")
API_TOKEN = os.getenv("TODOIST_API_TOKEN")
if not API_TOKEN:
    raise ValueError("TODOIST_API_TOKEN environment variable not set")

todoist = TodoistAPIAsync(API_TOKEN)


@mcp.tool()
async def todoist_get_tasks(
    project_id: Optional[str] = None,
    filter: Optional[str] = None
) -> str:
    """Get tasks from Todoist with optional filtering.

    Args:
        project_id: Filter tasks by project ID
        filter: Todoist filter query (e.g., "today", "p1", "overdue")

    Returns:
        Formatted list of tasks with IDs, content, due dates, and priorities
    """
    try:
        tasks = await todoist.get_tasks(project_id=project_id, filter=filter)

        if not tasks:
            return "No tasks found."

        result = f"Found {len(tasks)} task(s):\n\n"
        for task in tasks:
            result += f"- [{task.id}] {task.content}\n"
            if task.due:
                result += f"  Due: {task.due.string}\n"
            if task.priority > 1:
                priority_map = {4: "P1 (Urgent)", 3: "P2 (High)", 2: "P3 (Medium)"}
                result += f"  Priority: {priority_map.get(task.priority, task.priority)}\n"
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
    labels: Optional[List[str]] = None
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
            labels=labels
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
    labels: Optional[List[str]] = None
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
            labels=labels
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
        success = await todoist.close_task(task_id=task_id)
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
        projects = await todoist.get_projects()

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
        labels = await todoist.get_labels()

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
```

**Testing:**

```python
# tests/test_tools.py
import pytest
import os
from todoist_mcp.server import mcp

@pytest.mark.asyncio
async def test_all_tools_registered():
    """Verify all tools are properly registered"""
    # FastMCP automatically generates tool list from decorators
    # In actual implementation, you'd use MCP protocol to list tools
    pass


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_and_complete_task_flow():
    """Integration test for complete task workflow"""
    if not os.getenv("TODOIST_API_TOKEN"):
        pytest.skip("TODOIST_API_TOKEN not set")

    from todoist_api_python.api_async import TodoistAPIAsync
    todoist = TodoistAPIAsync(os.getenv("TODOIST_API_TOKEN"))

    # Create task
    task = await todoist.add_task(content="Test task from MCP server")
    assert task.id

    # Complete task
    success = await todoist.close_task(task_id=task.id)
    assert success

    # Cleanup (delete completed task)
    await todoist.delete_task(task_id=task.id)
```

### Step 5: Configuration and Documentation

**Files:**

- `README.md` - Usage instructions and setup guide
- `.env.example` - Environment variable template
- `docs/setup.md` - Detailed setup walkthrough
- `docs/api.md` - Tool reference documentation

**Changes:**

**README.md:**

````markdown
# Todoist MCP Server

An MCP (Model Context Protocol) server that enables AI agents to manage Todoist tasks.

## Features

- Create, read, update, and delete tasks
- Manage projects and labels
- Natural language due dates
- Priority and label support

## Installation

1. Clone the repository
2. Install dependencies: `pip install -e .`
3. Create `.env` file with your Todoist API token:
   `TODOIST_API_TOKEN=your_token_here`
4. Get your API token: <https://todoist.com/help/articles/find-your-api-token-Jpzx9IIlB>

## Usage with Claude Code

Add to your Claude Code MCP settings:

```json
{
  "mcpServers": {
    "todoist": {
      "command": "python",
      "args": ["-m", "todoist_mcp.server"],
      "env": {
        "TODOIST_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

## Available Tools

- `todoist_get_tasks` - Retrieve tasks with filtering
- `todoist_create_task` - Create new tasks
- `todoist_update_task` - Update existing tasks
- `todoist_complete_task` - Mark tasks as complete
- `todoist_delete_task` - Delete tasks
- `todoist_get_projects` - List all projects
- `todoist_get_labels` - List all labels

## Examples

Ask Claude Code:

- "Show me all my tasks due today"
- "Create a task to review the PR tomorrow with high priority"
- "Complete the task with ID 12345"
- "What projects do I have?"

## Development

See [docs/setup.md](docs/setup.md) for development setup.

Run tests: `pytest`

## License

MIT

````

**.env.example:**

```env
# Todoist API Token
# Get your token: https://todoist.com/help/articles/find-your-api-token-Jpzx9IIlB
TODOIST_API_TOKEN=your_api_token_here
```

**Testing:**

```bash
# Verify README renders correctly
# Verify .env.example has all required variables
# Test installation instructions on clean environment
```

### Step 6: Testing and Validation

**Files:**

- `tests/test_server.py` - Server initialization tests (FastMCP, tool registration)
- `tests/test_integration.py` - Integration tests with real Todoist API
- `.github/workflows/ci.yml` - CI pipeline updates

**Note:** Pytest configuration is in `pyproject.toml` (Step 1), not separate `pytest.ini` file.

**Changes:**

1. Write unit tests for server initialization and tool registration
2. Create integration tests with real Todoist account (marked with `@pytest.mark.integration`)
3. Use official `todoist-api-python` SDK in tests (no mocking needed for integration tests)
4. Update CI workflow to run unit tests (skip integration tests by default)
5. Achieve >80% test coverage on src/todoist_mcp

**Pytest Configuration (Already in pyproject.toml from Step 1):**

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
asyncio_mode = "auto"
addopts = "--cov=src/todoist_mcp --cov-report=term-missing --cov-fail-under=80"
```

**Testing:**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/todoist_mcp --cov-report=html

# Run integration tests only
pytest tests/test_integration.py

# Verify coverage meets threshold
pytest --cov-fail-under=80
```

### Step 7: Pre-commit Hooks and Code Quality

**Files:**

- `.pre-commit-config.yaml` - Update with Python hooks
- `pyproject.toml` - Add tool configurations

**Changes:**

1. Enable Python-specific pre-commit hooks:
   - `black` - Code formatting
   - `isort` - Import sorting
   - `flake8` - Linting
   - `mypy` - Type checking
2. Configure tools in pyproject.toml
3. Run pre-commit on all files
4. Fix any issues found

**.pre-commit-config.yaml additions:**

```yaml
  # Python
  - repo: https://github.com/psf/black
    rev: 24.10.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 7.1.1
    hooks:
      - id: flake8
        args: ["--max-line-length=88", "--extend-ignore=E203"]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.2
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

**Testing:**

```bash
# Install pre-commit
pre-commit install

# Run on all files
pre-commit run --all-files

# Verify no errors
```

## Detailed Testing Strategy

### Unit Testing

**Test Coverage Areas:**

1. **Server Initialization:** FastMCP setup, API token validation, error handling
2. **Tool Registration:** Verify all 7 tools are registered with correct schemas
3. **Error Handling:** Missing API token, invalid inputs, API errors

**Approach:**

- Test server initialization without real API calls
- Verify tool registration using FastMCP internals
- Test error paths (missing token, etc.)
- Keep unit tests fast (no external dependencies)

**Example Tests:**

```python
# tests/test_server.py
import pytest
import os

def test_server_requires_api_token(monkeypatch):
    """Test that server raises error without API token"""
    monkeypatch.delenv("TODOIST_API_TOKEN", raising=False)

    with pytest.raises(ValueError, match="TODOIST_API_TOKEN"):
        import todoist_mcp.server

def test_server_initializes_with_token(monkeypatch):
    """Test that server initializes properly with token"""
    monkeypatch.setenv("TODOIST_API_TOKEN", "test_token")

    from todoist_mcp.server import mcp, todoist
    assert mcp is not None
    assert todoist is not None

@pytest.mark.asyncio
async def test_tool_schemas_generated():
    """Test that FastMCP generates correct tool schemas"""
    # FastMCP automatically generates schemas from type hints
    # Verify tools exist and have expected parameters
    pass
```

**Note:** Unit tests focus on server initialization and registration. Integration tests (below) handle actual Todoist API calls.

### Integration Testing

**Test Case 1: Create and Retrieve Task**

1. Create a task with specific content
2. Retrieve all tasks
3. Verify created task appears in list
4. Clean up by deleting task

**Test Case 2: Update Task Priority**

1. Create a task with normal priority
2. Update task to urgent priority
3. Verify priority changed
4. Clean up

**Test Case 3: Complete Task Workflow**

1. Create a task
2. Mark as complete
3. Verify task no longer in active tasks
4. Clean up

**Setup:**

- Use dedicated test project in Todoist
- Store test project ID in environment
- Clean up all test tasks after each test
- Skip integration tests if no API token provided

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_and_retrieve_task(todoist_client, test_project_id):
    # Create task
    task = await todoist_client.create_task(
        content="Integration test task",
        project_id=test_project_id
    )
    task_id = task["id"]

    try:
        # Retrieve tasks
        tasks = await todoist_client.get_tasks(project_id=test_project_id)
        task_ids = [t["id"] for t in tasks]

        assert task_id in task_ids
    finally:
        # Cleanup
        await todoist_client.delete_task(task_id)
```

### Regression Testing

**Existing Functionality to Verify:**

- MCP server still starts correctly
- Tool registration works
- JSON-RPC communication functions
- Error responses follow MCP format

**Edge Cases:**

- Empty task list
- Invalid task IDs
- Malformed API responses
- Network timeouts
- Rate limiting (429 errors)
- Invalid API tokens

## Success Criteria

- [x] Research completed: MCP specification and Todoist API
- [ ] Python project structure created with dependencies
- [ ] MCP server initializes and responds to tool list requests
- [ ] Todoist API client successfully authenticates
- [ ] All 7 core tools implemented (get, create, update, complete, delete, projects, labels)
- [ ] Input validation using Pydantic schemas
- [ ] Error handling for API failures and invalid inputs
- [ ] Unit tests written and passing (>80% coverage)
- [ ] Integration tests with real Todoist account passing
- [ ] Pre-commit hooks configured and passing
- [ ] README with setup and usage instructions
- [ ] .env.example with API token template
- [ ] API documentation for all tools
- [ ] CI pipeline running tests on push
- [ ] Server successfully integrates with Claude Code

## Files Modified

### New Files Created

1. `src/todoist_mcp/__init__.py` - Package initialization
2. `src/todoist_mcp/server.py` - Complete MCP server implementation with all tools
3. `tests/__init__.py` - Test package
4. `tests/test_server.py` - Server initialization tests
5. `tests/test_integration.py` - Integration tests with real Todoist API
6. `tests/conftest.py` - Pytest fixtures
7. `pyproject.toml` - Python project configuration (includes all dependencies and tool config)
8. `.env.example` - Environment variable template
9. `docs/api.md` - Tool API documentation

**Note:** Using official SDKs (`mcp` and `todoist-api-python`) eliminates need for:

- ~~`todoist_client.py`~~ - Using `todoist-api-python` SDK directly
- ~~`tools.py`~~ - Tools defined inline in `server.py` with FastMCP decorators
- ~~`requirements.txt`~~ - Using `pyproject.toml` instead
- ~~`pytest.ini`~~ - Configuration in `pyproject.toml` under `[tool.pytest.ini_options]`

### Modified Files

1. `README.md` - Update with Todoist MCP server information
2. `.gitignore` - Add Python-specific patterns (.env, **pycache**, etc.)
3. `.pre-commit-config.yaml` - Add Python hooks (black, isort, flake8, mypy)
4. `.github/workflows/ci.yml` - Add Python testing step
5. `CLAUDE.md` - Update with project-specific information

## Related Issues and Tasks

### Depends On

- None (initial implementation)

### Blocks

- Future features: recurring tasks, task comments, collaboration features
- Advanced filtering and search capabilities
- OAuth implementation for multi-user support

### Related

- MCP specification: <https://modelcontextprotocol.io/specification/2025-06-18>
- Todoist REST API v2: <https://developer.todoist.com/rest/v2/>
- Official Todoist Python SDK: <https://github.com/Doist/todoist-api-python>

### Enables

- AI-powered task management workflows
- Natural language task creation and organization
- Integration with other MCP tools for productivity automation
- Voice-to-task workflows through Claude

## References

### Issue

- [GitHub Issue #1](https://github.com/denhamparry/todoist-mcp/issues/1)

### Documentation

- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/2025-06-18)
- [Todoist REST API v2 Reference](https://developer.todoist.com/rest/v2/)
- [Todoist Python SDK Documentation](https://doist.github.io/todoist-api-python/)
- [Find Todoist API Token](https://todoist.com/help/articles/find-your-api-token-Jpzx9IIlB)
- [MCP Python SDK Repository](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Server Examples](https://github.com/modelcontextprotocol/servers)

### Research Sources

- [Model Context Protocol - Wikipedia](https://en.wikipedia.org/wiki/Model_Context_Protocol)
- [Anthropic MCP Announcement](https://www.anthropic.com/news/model-context-protocol)
- [MCP 2025 Guide](https://quashbugs.com/blog/model-context-protocol-mcp-guide)
- [MCP Specification Updates June 2025](https://auth0.com/blog/mcp-specs-update-all-about-auth/)

## Implementation Decisions

Based on the plan review, the following technical decisions have been made:

### 1. Package Manager: `uv` (Recommended) with `pip` Fallback

**Decision:** Provide both options, recommend `uv`

**Rationale:**

- `uv` is the modern Python package manager recommended by the MCP ecosystem
- Significantly faster dependency resolution (10-100x faster than pip)
- Better dependency locking and reproducibility
- However, `pip` is more universally available and familiar
- Provide both options to accommodate different developer preferences and CI/CD systems

**Implementation:** Step 1 includes both Option A (uv) and Option B (pip) with clear instructions

### 2. MCP SDK Pattern: FastMCP (High-Level API)

**Decision:** Use FastMCP instead of low-level Server class

**Rationale:**

- FastMCP is simpler and more intuitive for most use cases
- Automatically generates tool schemas from type hints
- Reduces boilerplate code significantly (~50% less code)
- Better developer experience with decorator-based API
- Handles stdio transport automatically
- Low-level Server API provided as alternative for advanced use cases

**Code Impact:**

```python
# FastMCP (chosen) - ~5 lines to add a tool
@mcp.tool()
async def my_tool(param: str) -> str:
    """Docstring becomes tool description"""
    return result

# vs Server (alternative) - ~15 lines to add a tool
@app.list_tools()
async def list_tools():
    return [Tool(name="my_tool", description="...", inputSchema={...})]

@app.call_tool()
async def call_tool(name: str, args: dict):
    if name == "my_tool":
        ...
```

**Implementation:** Step 2 demonstrates FastMCP with low-level alternative provided

### 3. HTTP Client: Official Todoist SDK

**Decision:** Use `todoist-api-python` instead of building custom HTTP client with `httpx`

**Rationale:**

- Official SDK maintained by Todoist team (Doist)
- Eliminates ~200+ lines of custom HTTP client code
- Built-in error handling, retries, and authentication
- Type hints and IDE autocomplete support
- Async support included (`TodoistAPIAsync`)
- Automatically updated when Todoist API changes
- Well-tested and battle-tested in production
- Reduces maintenance burden and potential bugs

**Code Impact:**

- Eliminates `todoist_client.py` file entirely
- Reduces Step 3 from custom implementation to SDK usage documentation
- Changes dependency from `httpx` to `todoist-api-python>=2.1.9`

**Implementation:** Step 3 simplified to SDK usage guide

### 4. API Version: REST API v2

**Decision:** Use REST API v2 exclusively

**Rationale:**

- REST API v1 was sunset in November 2022 (no longer available)
- All new development must use v2
- Base URL: `https://api.todoist.com/rest/v2/`
- Key difference: IDs are strings in v2 (were integers in v1)
- Official SDK uses v2 by default

**Implementation:** All references updated to v2 throughout plan

### 5. Python Version: >=3.10

**Decision:** Require Python 3.10 or later

**Rationale:**

- MCP SDK works with Python 3.9+ but 3.10+ recommended
- Better type hint support (PEP 604: Union types with `|`)
- Improved async/await error messages
- Pattern matching (PEP 634) available if needed
- Most systems have 3.10+ by late 2025

**Implementation:** `requires-python = ">=3.10"` in pyproject.toml

### 6. Testing Strategy: TDD with Separate Integration Tests

**Decision:** Write tests first, separate unit and integration tests

**Rationale:**

- TDD enforced by project template and CLAUDE.md
- Unit tests: Mock SDK responses, fast, no API calls
- Integration tests: Real API calls, marked with `@pytest.mark.integration`
- Integration tests skipped in CI by default (require API token)
- Can run integration tests manually during development

**Markers:**

```python
@pytest.mark.asyncio  # All async tests
@pytest.mark.integration  # Requires real API token
```

**Implementation:**

- Unit tests in `tests/test_server.py`
- Integration tests in `tests/test_integration.py`
- pytest.ini configured in pyproject.toml

### 7. Project Structure: Minimal, Single-File Server

**Decision:** Keep server implementation in single file initially

**Rationale:**

- FastMCP encourages single-file servers for simple use cases
- ~300 lines total for complete implementation
- Easier to understand and maintain
- Can refactor into modules later if needed
- Follows MCP community patterns

**Structure:**

```text
todoist-mcp/
├── src/
│   └── todoist_mcp/
│       ├── __init__.py
│       └── server.py  # Complete implementation
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_server.py
│   └── test_integration.py
├── pyproject.toml
├── .env.example
└── README.md
```

### 8. Documentation: README-First Approach

**Decision:** Create comprehensive README during Step 5

**Rationale:**

- README serves as primary documentation
- Includes installation, setup, usage examples
- Configuration instructions for Claude Code
- Follows project template guidelines
- API documentation in separate `docs/api.md` for reference

**Implementation:** Step 5 includes complete README template

## Notes

### Key Insights

1. **MCP is JSON-RPC based:** Leverage existing JSON-RPC libraries, focus on tool implementation
2. **Python SDK available:** Official support makes implementation straightforward
3. **Todoist REST API is simple:** Well-documented, RESTful, easy to integrate
4. **stdio transport recommended:** Simpler than HTTP for local Claude Code integration
5. **Natural language dates:** Todoist supports "tomorrow", "next week" - pass through directly
6. **Rate limiting:** Todoist API has rate limits, implement exponential backoff

### Alternative Approaches Considered

1. **Language Choice:**
   - **TypeScript** ❌: More boilerplate, Node.js runtime required
   - **Go** ❌: No official MCP SDK, manual JSON-RPC implementation needed
   - **Python** ✅: Official MCP SDK, excellent async support, rapid development

2. **MCP SDK Pattern:**
   - **Low-level Server API** ❌: More control but significantly more boilerplate
   - **FastMCP** ✅: Simpler, decorator-based, auto-generates schemas, less code

3. **HTTP Client:**
   - **Custom httpx client** ❌: ~200 lines of code, maintenance burden, potential bugs
   - **Official todoist-api-python SDK** ✅: Maintained by Todoist, built-in features, well-tested

4. **Package Manager:**
   - **pip only** ❌: Slower, less reproducible
   - **poetry** ❌: Complex, overkill for this project
   - **uv** ✅: Fast, modern, MCP ecosystem standard (with pip fallback for compatibility)

5. **API Version:**
   - **REST API v1** ❌: Sunset in November 2022, no longer available
   - **REST API v2** ✅: Current version, only option for new development

6. **Transport:**
   - **HTTP** ❌: More complex, requires server deployment
   - **stdio** ✅: Simpler for local Claude Code integration, MCP standard

7. **Project Structure:**
   - **Multi-file modules** ❌: Premature complexity for ~300 lines
   - **Single-file server** ✅: Easier to understand, follows FastMCP patterns

### Best Practices

1. **TDD Approach:** Write tests before implementation for all tools
2. **Security:** Never commit API tokens, use environment variables
3. **Error Handling:** Provide clear, actionable error messages to AI agent
4. **Documentation:** Include examples in README for common use cases
5. **Testing:** Maintain separate test project in Todoist for integration tests
6. **Rate Limiting:** Respect API limits, implement retry logic with exponential backoff
7. **Type Safety:** Use Pydantic for input validation and type checking
8. **Async:** Use async/await throughout for better performance
9. **Logging:** Add logging for debugging without exposing sensitive data
10. **Versioning:** Follow semantic versioning for releases

### Implementation Tips

1. Start with minimal tool set (get, create) and expand
2. Test each component independently before integration
3. Use pytest fixtures for reusable test setup
4. Mock HTTP responses in unit tests to avoid API rate limits
5. Keep integration tests separate with `@pytest.mark.integration`
6. Document expected input/output format for each tool
7. Format responses for readability (markdown lists, bullet points)
8. Include task IDs in responses for follow-up operations
9. Support both project names and IDs for flexibility
10. Provide helpful error messages when API token is missing/invalid

### Monitoring and Observability

1. **Logging:** Use Python logging module with appropriate levels
2. **Metrics:** Consider tracking API call counts and latency
3. **Error Tracking:** Log API errors with context (status code, response)
4. **Performance:** Monitor task creation/retrieval times
5. **Rate Limits:** Track 429 responses and retry behavior

### Future Enhancements

1. **Task Comments:** Add support for adding/reading comments
2. **Recurring Tasks:** Support recurring task creation
3. **Collaboration:** Assign tasks, share projects
4. **Advanced Filtering:** Complex filter queries
5. **Batch Operations:** Create/update multiple tasks at once
6. **Webhooks:** Real-time task updates
7. **OAuth Support:** Multi-user authentication
8. **Caching:** Cache projects/labels to reduce API calls
9. **Offline Support:** Queue operations when offline
10. **Rich Formatting:** Support Markdown in task descriptions
