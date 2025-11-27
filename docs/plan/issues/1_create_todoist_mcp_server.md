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

- REST API v1: <https://developer.todoist.com/rest/v1/>
- Authentication: Bearer token (personal or OAuth)
- Main endpoints needed:
  - Tasks: GET, POST, PUT, DELETE `/rest/v1/tasks`
  - Projects: GET `/rest/v1/projects`
  - Labels: GET `/rest/v1/labels`
  - Comments: GET, POST `/rest/v1/comments`

## Solution Design

### Approach

Build a Python-based MCP server using the official MCP SDK that exposes Todoist task management capabilities as MCP tools. Python chosen for:

1. Official MCP SDK support
2. Rapid development and iteration
3. Excellent HTTP client libraries (httpx, requests)
4. Strong community support
5. Easy testing with pytest

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
│  └───────────┘  │
└────────┬────────┘
         │
         │ HTTPS REST API
         │
┌────────▼────────┐
│  Todoist API    │
│  (REST v1)      │
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

- `pyproject.toml` - Python project configuration
- `requirements.txt` or `poetry.lock` - Dependencies
- `.env.example` - Environment template
- `.gitignore` - Ignore .env, **pycache**, etc.

**Changes:**

1. Initialize Python project structure
2. Add dependencies:
   - `mcp` - Official MCP SDK
   - `httpx` - Modern HTTP client
   - `python-dotenv` - Environment variable management
   - `pydantic` - Data validation
   - `pytest` - Testing framework
   - `pytest-asyncio` - Async test support
   - `pytest-cov` - Coverage reporting

**Testing:**

```bash
# Verify dependencies install
python -m pip install -e .

# Verify imports work
python -c "import mcp; import httpx; import dotenv"
```

### Step 2: Create MCP Server Foundation

**File:** `src/todoist_mcp/server.py`

**Changes:**

1. Create MCP server class
2. Initialize server with name and version
3. Set up stdio transport
4. Add configuration loading (API token)
5. Implement server lifecycle (startup, shutdown)

**Code Example:**

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
import os
from dotenv import load_dotenv

load_dotenv()

app = Server("todoist-mcp")

@app.list_tools()
async def list_tools():
    """List available Todoist tools"""
    return [
        {
            "name": "todoist_get_tasks",
            "description": "Get tasks from Todoist",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string"},
                    "filter": {"type": "string"}
                }
            }
        }
    ]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

**Testing:**

```bash
# Run server (should not crash)
python -m todoist_mcp.server

# Verify server responds to list_tools
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python -m todoist_mcp.server
```

### Step 3: Implement Todoist API Client

**File:** `src/todoist_mcp/todoist_client.py`

**Changes:**

1. Create `TodoistClient` class
2. Initialize with API token
3. Implement HTTP methods (GET, POST, PUT, DELETE)
4. Add methods for each API endpoint:
   - `get_tasks(project_id=None, filter=None)`
   - `create_task(content, **kwargs)`
   - `update_task(task_id, **kwargs)`
   - `complete_task(task_id)`
   - `delete_task(task_id)`
   - `get_projects()`
   - `get_labels()`
5. Error handling and response parsing

**Code Example:**

```python
import httpx
from typing import Optional, List, Dict, Any

class TodoistClient:
    BASE_URL = "https://api.todoist.com/rest/v2"

    def __init__(self, api_token: str):
        self.api_token = api_token
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )

    async def get_tasks(
        self,
        project_id: Optional[str] = None,
        filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get tasks from Todoist"""
        params = {}
        if project_id:
            params["project_id"] = project_id
        if filter:
            params["filter"] = filter

        response = await self.client.get(f"{self.BASE_URL}/tasks", params=params)
        response.raise_for_status()
        return response.json()

    async def create_task(
        self,
        content: str,
        description: Optional[str] = None,
        project_id: Optional[str] = None,
        due_string: Optional[str] = None,
        priority: Optional[int] = None,
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a new task"""
        data = {"content": content}
        if description:
            data["description"] = description
        if project_id:
            data["project_id"] = project_id
        if due_string:
            data["due_string"] = due_string
        if priority:
            data["priority"] = priority
        if labels:
            data["labels"] = labels

        response = await self.client.post(f"{self.BASE_URL}/tasks", json=data)
        response.raise_for_status()
        return response.json()

    # Additional methods: update_task, complete_task, delete_task, get_projects, get_labels
```

**Testing:**

```python
# tests/test_todoist_client.py
import pytest
from todoist_mcp.todoist_client import TodoistClient

@pytest.mark.asyncio
async def test_get_tasks(mock_httpx_client):
    client = TodoistClient("test_token")
    tasks = await client.get_tasks()
    assert isinstance(tasks, list)

@pytest.mark.asyncio
async def test_create_task(mock_httpx_client):
    client = TodoistClient("test_token")
    task = await client.create_task("Test task")
    assert task["content"] == "Test task"
```

### Step 4: Implement MCP Tool Handlers

**File:** `src/todoist_mcp/tools.py`

**Changes:**

1. Create tool handler functions for each Todoist operation
2. Connect tool handlers to MCP server
3. Implement input validation using Pydantic
4. Format responses for AI agent consumption
5. Error handling and user-friendly messages

**Code Example:**

```python
from mcp.server import Server
from pydantic import BaseModel, Field
from typing import Optional, List
from .todoist_client import TodoistClient

class GetTasksInput(BaseModel):
    project_id: Optional[str] = Field(None, description="Filter tasks by project ID")
    filter: Optional[str] = Field(None, description="Todoist filter query")

class CreateTaskInput(BaseModel):
    content: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    project_id: Optional[str] = Field(None, description="Project ID")
    due_string: Optional[str] = Field(None, description="Due date (e.g., 'tomorrow', 'next Monday')")
    priority: Optional[int] = Field(None, ge=1, le=4, description="Priority (1=normal, 4=urgent)")
    labels: Optional[List[str]] = Field(None, description="Label names")

def register_tools(server: Server, todoist: TodoistClient):
    @server.call_tool()
    async def todoist_get_tasks(arguments: dict) -> str:
        """Get tasks from Todoist"""
        input_data = GetTasksInput(**arguments)
        tasks = await todoist.get_tasks(
            project_id=input_data.project_id,
            filter=input_data.filter
        )

        # Format for readability
        result = f"Found {len(tasks)} tasks:\n\n"
        for task in tasks:
            result += f"- [{task['id']}] {task['content']}\n"
            if task.get('due'):
                result += f"  Due: {task['due']['string']}\n"
            if task.get('priority') > 1:
                result += f"  Priority: {task['priority']}\n"

        return result

    @server.call_tool()
    async def todoist_create_task(arguments: dict) -> str:
        """Create a new task in Todoist"""
        input_data = CreateTaskInput(**arguments)
        task = await todoist.create_task(
            content=input_data.content,
            description=input_data.description,
            project_id=input_data.project_id,
            due_string=input_data.due_string,
            priority=input_data.priority,
            labels=input_data.labels
        )

        return f"Task created successfully: {task['content']} (ID: {task['id']})"

    # Additional tool handlers: update, complete, delete, get_projects, get_labels
```

**Testing:**

```python
# tests/test_tools.py
import pytest
from todoist_mcp.tools import register_tools
from todoist_mcp.server import app

@pytest.mark.asyncio
async def test_todoist_get_tasks_tool():
    # Test tool is registered
    tools = await app.list_tools()
    assert any(t["name"] == "todoist_get_tasks" for t in tools)

@pytest.mark.asyncio
async def test_todoist_create_task_tool(mock_todoist_client):
    result = await app.call_tool("todoist_create_task", {
        "content": "Test task"
    })
    assert "Task created successfully" in result
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

- `tests/test_server.py` - Server initialization tests
- `tests/test_todoist_client.py` - API client tests
- `tests/test_tools.py` - Tool handler tests
- `tests/test_integration.py` - End-to-end tests
- `pytest.ini` - Pytest configuration
- `.github/workflows/ci.yml` - CI pipeline updates

**Changes:**

1. Write comprehensive unit tests for all components
2. Create integration tests with real Todoist account
3. Set up pytest configuration with coverage
4. Update CI workflow to run tests
5. Achieve >80% test coverage

**pytest.ini:**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --cov=src/todoist_mcp
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
asyncio_mode = auto
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

1. **TodoistClient:** All HTTP methods, error handling, response parsing
2. **Tool Handlers:** Input validation, response formatting, error messages
3. **Server:** Initialization, tool registration, lifecycle

**Approach:**

- Mock HTTP responses using `pytest-httpx`
- Test success and error cases
- Validate input schemas with invalid data
- Verify error messages are user-friendly

**Example Test:**

```python
@pytest.mark.asyncio
async def test_get_tasks_with_filter(httpx_mock):
    httpx_mock.add_response(
        url="https://api.todoist.com/rest/v2/tasks?filter=today",
        json=[{"id": "123", "content": "Test task"}]
    )

    client = TodoistClient("test_token")
    tasks = await client.get_tasks(filter="today")

    assert len(tasks) == 1
    assert tasks[0]["content"] == "Test task"
```

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
2. `src/todoist_mcp/server.py` - MCP server implementation
3. `src/todoist_mcp/todoist_client.py` - Todoist API client
4. `src/todoist_mcp/tools.py` - MCP tool handlers
5. `tests/__init__.py` - Test package
6. `tests/test_server.py` - Server tests
7. `tests/test_todoist_client.py` - Client tests
8. `tests/test_tools.py` - Tool tests
9. `tests/test_integration.py` - Integration tests
10. `tests/conftest.py` - Pytest fixtures
11. `pyproject.toml` - Python project configuration
12. `requirements.txt` - Production dependencies
13. `requirements-dev.txt` - Development dependencies
14. `.env.example` - Environment template
15. `pytest.ini` - Pytest configuration
16. `docs/api.md` - Tool API documentation

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
- Todoist REST API: <https://developer.todoist.com/rest/v1/>

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
- [Todoist REST API Reference](https://developer.todoist.com/rest/v1/)
- [Find Todoist API Token](https://www.todoist.com/help/articles/find-your-api-token-Jpzx9IIlB)
- [MCP GitHub Repository](https://github.com/modelcontextprotocol)
- [MCP Server Examples](https://github.com/modelcontextprotocol/servers)

### Research Sources

- [Model Context Protocol - Wikipedia](https://en.wikipedia.org/wiki/Model_Context_Protocol)
- [Anthropic MCP Announcement](https://www.anthropic.com/news/model-context-protocol)
- [MCP 2025 Guide](https://quashbugs.com/blog/model-context-protocol-mcp-guide)
- [MCP Specification Updates June 2025](https://auth0.com/blog/mcp-specs-update-all-about-auth/)

## Notes

### Key Insights

1. **MCP is JSON-RPC based:** Leverage existing JSON-RPC libraries, focus on tool implementation
2. **Python SDK available:** Official support makes implementation straightforward
3. **Todoist REST API is simple:** Well-documented, RESTful, easy to integrate
4. **stdio transport recommended:** Simpler than HTTP for local Claude Code integration
5. **Natural language dates:** Todoist supports "tomorrow", "next week" - pass through directly
6. **Rate limiting:** Todoist API has rate limits, implement exponential backoff

### Alternative Approaches Considered

1. **TypeScript Implementation** ❌
   - Pros: Strong typing, official SDK, good for frontend developers
   - Cons: More boilerplate than Python, requires Node.js runtime
   - Why not chosen: Python is simpler for rapid prototyping and has better async support

2. **Go Implementation** ❌
   - Pros: Fast, single binary distribution, strong typing
   - Cons: No official MCP SDK, would need to implement JSON-RPC manually
   - Why not chosen: More development effort, no SDK support

3. **Python with Flask/FastAPI** ❌
   - Pros: HTTP transport, web-based interface possible
   - Cons: More complex than stdio, requires server deployment
   - Why not chosen: stdio is simpler for local Claude Code use case

4. **Python with MCP SDK (stdio)** ✅
   - Pros: Official SDK, simple setup, async support, rapid development
   - Cons: Requires Python runtime
   - Why chosen: Best balance of simplicity, official support, and development speed

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
