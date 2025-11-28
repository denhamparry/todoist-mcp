# Troubleshooting Guide

This guide helps you diagnose and fix common issues with the Todoist MCP server.

## Table of Contents

- [Quick Troubleshooting Checklist](#quick-troubleshooting-checklist)
- [Setup Issues](#setup-issues)
  - [API Token Not Found](#api-token-not-found)
  - [Import/Module Errors](#importmodule-errors)
  - [Invalid API Token](#invalid-api-token)
- [Runtime Issues](#runtime-issues)
  - [Invalid Task ID Errors](#invalid-task-id-errors)
  - [Rate Limit Errors (429)](#rate-limit-errors-429)
  - [Validation Errors](#validation-errors)
  - [Project/Label Not Found](#projectlabel-not-found)
- [MCP Integration Issues](#mcp-integration-issues)
  - [Server Not Appearing in Claude Desktop](#server-not-appearing-in-claude-desktop)
  - [Server Crashes on Startup](#server-crashes-on-startup)
  - [Server Connection Errors](#server-connection-errors)
  - [Environment Variables Not Loading](#environment-variables-not-loading)
- [Debugging Techniques](#debugging-techniques)
  - [Using Log Levels](#using-log-levels)
  - [Testing with MCP Inspector](#testing-with-mcp-inspector)
  - [Manual Server Testing](#manual-server-testing)
  - [Running Unit Tests](#running-unit-tests)
  - [Verifying API Token Manually](#verifying-api-token-manually)
- [FAQ](#faq)
- [See Also](#see-also)
- [Getting Help](#getting-help)

## Quick Troubleshooting Checklist

Before diving into detailed troubleshooting, try these quick checks:

1. **API Token**: Is `TODOIST_API_TOKEN` set in your `.env` file or MCP config?
2. **Dependencies**: Have you run `uv sync` or `pip install -e ".[dev]"`?
3. **Python Version**: Are you using Python 3.10 or higher?
4. **Configuration**: Is your Claude Desktop MCP configuration valid JSON?
5. **Logs**: Have you checked the server logs with `LOG_LEVEL=DEBUG`?

If the issue persists, continue to the relevant section below.

## Setup Issues

### API Token Not Found

**Symptom:**

```text
TODOIST_API_TOKEN environment variable not set
```

**Cause:**

The Todoist API token is missing or incorrectly configured in your environment.

**Solution:**

1. Create a `.env` file in the project root if it doesn't exist:

   ```bash
   cp .env.example .env
   ```

2. Get your API token from Todoist:
   - Go to [Todoist Settings](https://todoist.com/prefs/integrations)
   - Find your API token under "Integrations" → "Developer"
   - Copy the token

3. Add the token to your `.env` file:

   ```bash
   TODOIST_API_TOKEN=your_actual_token_here
   ```

4. For MCP usage, add the token to your Claude Desktop configuration:

   ```json
   {
     "mcpServers": {
       "todoist": {
         "command": "uv",
         "args": ["run", "python", "-m", "todoist_mcp.server"],
         "env": {
           "TODOIST_API_TOKEN": "your_actual_token_here"
         }
       }
     }
   }
   ```

**Verification:**

```bash
# Check that token is in .env file
grep TODOIST_API_TOKEN .env

# Verify it's not empty
echo $TODOIST_API_TOKEN
```

**See:** [Todoist API Token Guide](https://todoist.com/help/articles/find-your-api-token-Jpzx9IIlB)

### Import/Module Errors

**Symptom:**

```text
ModuleNotFoundError: No module named 'mcp'
ModuleNotFoundError: No module named 'todoist_api_python'
```

**Cause:**

Required dependencies are not installed in your Python environment.

**Solution:**

1. Using `uv` (recommended):

   ```bash
   uv sync
   ```

2. Using `pip`:

   ```bash
   pip install -e ".[dev]"
   ```

3. Verify installation:

   ```bash
   # Check pytest is available
   pytest --version

   # Check Python can import the module
   python -c "import mcp; print('MCP installed successfully')"
   python -c "import todoist_api_python; print('Todoist API installed successfully')"
   ```

**Verification:**

```bash
# Run a simple test to verify everything is working
pytest tests/test_server.py::test_validate_task_id -v
```

### Invalid API Token

**Symptom:**

```text
401 Unauthorized
Authentication failed
```

**Cause:**

The API token is incorrect, expired, has typos, or lacks required permissions.

**Solution:**

1. Verify your token in Todoist:
   - Go to [Todoist Settings → Integrations](https://todoist.com/prefs/integrations)
   - Check if the token matches exactly what's in your `.env` file
   - Look for extra spaces, newlines, or special characters

2. If unsure, regenerate the token:
   - In Todoist Settings, revoke the old token
   - Generate a new token
   - Update your `.env` file with the new token

3. Test the token manually:

   ```bash
   # Test with curl
   curl -H "Authorization: Bearer $TODOIST_API_TOKEN" \
        https://api.todoist.com/rest/v2/projects

   # Should return JSON array of projects, not 401 error
   ```

4. Restart the MCP server or Claude Desktop after updating the token

**Verification:**

```bash
# Run integration test to verify token works
pytest tests/integration/test_integration.py::test_get_tasks -v
```

**See:** [Todoist API Authentication](https://developer.todoist.com/rest/v2/#authorization)

## Runtime Issues

### Invalid Task ID Errors

**Symptom:**

```text
Task ID does not exist
404 Not Found
```

**Cause:**

The task ID is incorrect, the task was deleted, or you don't have access to it.

**Solution:**

1. First, get a list of all your tasks:

   ```text
   Use the todoist_get_tasks tool in Claude Desktop
   ```

2. Copy the exact task ID from the results (format: `"1234567890"`)

3. Verify the task exists in Todoist web app

4. Make sure you're using the task ID as a string, not a number

**Example:**

```text
# Correct usage in Claude Desktop:
"Please update task 1234567890 to set priority to 4"

# Get tasks first to find the ID:
"Show me all my tasks"
# Then use the ID from the results
```

**Common Mistakes:**

- Using project ID instead of task ID
- Copy-pasting with extra spaces or quotes
- Task was recently deleted but still cached in Claude

**See:** `docs/api.md` for task management details

### Rate Limit Errors (429)

**Symptom:**

```text
Todoist API rate limit exceeded (429)
Please wait 15 minutes before retrying
```

**Cause:**

Too many API requests in a 15-minute window. Standard Todoist plans allow approximately 450 requests per 15 minutes.

**Solution:**

1. **Immediate:** Wait 15 minutes before making more requests

2. **Prevention:**
   - Batch operations when possible
   - Avoid rapid-fire task creation/updates
   - Use filters to reduce the number of queries
   - Consider upgrading Todoist plan for higher limits

3. **Check current usage:**
   - The server logs rate limit headers from Todoist API
   - Enable DEBUG logging to see rate limit info:

     ```bash
     LOG_LEVEL=DEBUG uv run python -m todoist_mcp.server
     ```

**Rate Limit Details:**

- **Limit:** ~450 requests per 15 minutes (standard plan)
- **Window:** Rolling 15-minute window
- **Headers:** Server logs `X-RateLimit-Remaining` header

**Monitoring:**

The server automatically detects and logs when you're approaching rate limits:

```text
Rate limit remaining: 100 requests in current window
```

**See:** `docs/api.md` for rate limit handling details

### Validation Errors

The server validates all inputs before sending to the Todoist API. Here are common validation errors:

#### Priority Validation

**Symptom:**

```text
Priority must be between 1 and 4
```

**Cause:**

Invalid priority value (not 1-4).

**Solution:**

Use valid priority values:

- `1` = Normal (default)
- `2` = Medium
- `3` = High
- `4` = Urgent

**Example:**

```text
# Correct:
"Set task 1234567890 to priority 4"

# Incorrect:
"Set task 1234567890 to priority 5"  # Priority must be 1-4
```

#### Task ID Validation

**Symptom:**

```text
Task ID cannot be empty
Task ID must be a string
```

**Cause:**

Missing or invalid task ID.

**Solution:**

Always provide a valid task ID as a string:

```text
# Correct:
"Update task 1234567890"

# Incorrect:
"Update task"  # Missing ID
```

#### Labels Validation

**Symptom:**

```text
Labels must be a list of strings
```

**Cause:**

Labels provided in wrong format.

**Solution:**

Labels must be a list/array of strings:

```text
# Correct:
"Add labels 'urgent' and 'work' to task 1234567890"

# The server expects: ["urgent", "work"]
```

### Project/Label Not Found

**Symptom:**

```text
404 Not Found
Project does not exist
Label does not exist
```

**Cause:**

Invalid project or label ID, or the project/label was deleted.

**Solution:**

1. **For Projects:**

   ```text
   # In Claude Desktop, first list all projects:
   "Show me all my Todoist projects"

   # Then use the exact project ID from the results
   ```

2. **For Labels:**

   ```text
   # List all available labels:
   "Show me all my Todoist labels"

   # Use the exact label name (case-sensitive)
   ```

3. **Verify in Todoist Web App:**
   - Check if the project/label exists
   - Check spelling and capitalization
   - Check if you have access (not in a shared project you left)

**See:** Use `todoist_get_projects` and `todoist_get_labels` tools to find valid IDs

## MCP Integration Issues

### Server Not Appearing in Claude Desktop

**Symptom:**

The Todoist MCP server is not listed in Claude Desktop's available servers.

**Cause:**

Incorrect configuration file location, invalid JSON syntax, or configuration not loaded.

**Solution:**

1. **Find your Claude Desktop config file:**

   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux:** `~/.config/Claude/claude_desktop_config.json`

2. **Verify JSON syntax:**

   ```bash
   # Validate JSON (on macOS/Linux)
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | jq .

   # Should output formatted JSON, not a syntax error
   ```

3. **Ensure correct configuration:**

   ```json
   {
     "mcpServers": {
       "todoist": {
         "command": "uv",
         "args": [
           "run",
           "--directory",
           "/absolute/path/to/todoist-mcp",
           "python",
           "-m",
           "todoist_mcp.server"
         ],
         "env": {
           "TODOIST_API_TOKEN": "your_token_here"
         }
       }
     }
   }
   ```

4. **Use absolute paths:**
   - Replace `/absolute/path/to/todoist-mcp` with the actual absolute path
   - Run `pwd` in the todoist-mcp directory to get the path

5. **Restart Claude Desktop:**
   - Quit Claude Desktop completely
   - Restart it
   - Check if the server appears

**Verification:**

```bash
# Check if config file exists
ls -la ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Validate JSON syntax
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | jq .
```

**See:** `README.md` for complete installation instructions

### Server Crashes on Startup

**Symptom:**

Server immediately exits when Claude Desktop tries to launch it.

**Cause:**

Missing environment variables, wrong Python version, import errors, or invalid configuration.

**Solution:**

1. **Test manually to see the error:**

   ```bash
   cd /path/to/todoist-mcp
   TODOIST_API_TOKEN=your_token uv run python -m todoist_mcp.server
   ```

   This will show the actual error message.

2. **Common causes and fixes:**

   **Missing API Token:**

   ```bash
   # Add token to environment
   export TODOIST_API_TOKEN=your_token_here
   uv run python -m todoist_mcp.server
   ```

   **Wrong Python Version:**

   ```bash
   # Check Python version (needs 3.10+)
   python --version

   # Use uv to manage Python version automatically
   uv sync
   ```

   **Import Errors:**

   ```bash
   # Reinstall dependencies
   uv sync
   # or
   pip install -e ".[dev]"
   ```

3. **Check Claude Desktop logs:**
   - Logs are usually in stderr
   - Enable debug logging in config:

     ```json
     {
       "mcpServers": {
         "todoist": {
           "env": {
             "LOG_LEVEL": "DEBUG",
             "TODOIST_API_TOKEN": "your_token"
           }
         }
       }
     }
     ```

**Verification:**

```bash
# Server should start without errors
TODOIST_API_TOKEN=your_token uv run python -m todoist_mcp.server

# You'll see MCP protocol messages (JSON) on stdout
# Logs go to stderr
```

### Server Connection Errors

**Symptom:**

Claude Desktop can't connect to the MCP server, or server process is not responding.

**Cause:**

Server process not running, communication protocol errors, or path issues.

**Solution:**

1. **Verify command path is correct:**

   ```bash
   # Make sure 'uv' is in your PATH
   which uv

   # If not found, install uv or use absolute path in config
   ```

2. **Check directory path:**

   ```json
   {
     "mcpServers": {
       "todoist": {
         "args": [
           "run",
           "--directory",
           "/absolute/path/to/todoist-mcp",  // Must be absolute!
           "python",
           "-m",
           "todoist_mcp.server"
         ]
       }
     }
   }
   ```

3. **Test connection manually:**

   ```bash
   # Run server and test with MCP Inspector
   npx @modelcontextprotocol/inspector uv run python -m todoist_mcp.server
   ```

4. **Check for port conflicts:**
   - MCP uses stdio (stdin/stdout), not network ports
   - Ensure no other process is interfering with stdio

**Verification:**

Use MCP Inspector to verify server responds correctly (see [Testing with MCP Inspector](#testing-with-mcp-inspector))

### Environment Variables Not Loading

**Symptom:**

API token errors despite having `TODOIST_API_TOKEN` in the MCP configuration.

**Cause:**

Environment variables in MCP config are not being applied to the server process.

**Solution:**

1. **Ensure correct env format in config:**

   ```json
   {
     "mcpServers": {
       "todoist": {
         "command": "uv",
         "args": ["run", "python", "-m", "todoist_mcp.server"],
         "env": {
           "TODOIST_API_TOKEN": "your_actual_token_here",
           "LOG_LEVEL": "DEBUG"
         }
       }
     }
   }
   ```

2. **Avoid shell variables in config:**

   ```json
   // INCORRECT - Shell variables don't work in JSON
   "env": {
     "TODOIST_API_TOKEN": "$MY_TOKEN"
   }

   // CORRECT - Use actual value
   "env": {
     "TODOIST_API_TOKEN": "your_actual_token_here"
   }
   ```

3. **Alternative: Use .env file with uv:**

   If you prefer to keep token in `.env` file:

   - Create `.env` file in project directory
   - Add `TODOIST_API_TOKEN=your_token`
   - `uv` will automatically load it

4. **Verify environment variables are set:**

   ```bash
   # Add debug logging to server.py to verify env vars are loaded
   LOG_LEVEL=DEBUG uv run python -m todoist_mcp.server
   # Check logs for "Configuration loaded" message
   ```

**Security Note:**

- Never commit the MCP config file with real tokens to version control
- Keep tokens in `.env` file (which is gitignored)
- For Claude Desktop, you must put the token in the config since `.env` may not be loaded

## Debugging Techniques

### Using Log Levels

The server uses Python's logging module with configurable log levels.

**Available Log Levels:**

- `DEBUG` - Detailed diagnostic information (tool calls, API requests, validation)
- `INFO` - General informational messages (default)
- `WARNING` - Warning messages (approaching rate limits, deprecated features)
- `ERROR` - Error messages with stack traces
- `CRITICAL` - Critical errors that prevent server operation

**How to Enable Debug Logging:**

**Option 1: Using .env file (for local testing)**

```bash
# In .env file
LOG_LEVEL=DEBUG

# Run server
uv run python -m todoist_mcp.server
```

**Option 2: Using environment variable (for single run)**

```bash
# On macOS/Linux
LOG_LEVEL=DEBUG uv run python -m todoist_mcp.server

# On Windows (PowerShell)
$env:LOG_LEVEL="DEBUG"; uv run python -m todoist_mcp.server
```

**Option 3: In Claude Desktop MCP config**

```json
{
  "mcpServers": {
    "todoist": {
      "env": {
        "LOG_LEVEL": "DEBUG",
        "TODOIST_API_TOKEN": "your_token"
      }
    }
  }
}
```

**What Debug Logs Show:**

```text
2025-11-28 10:15:32 - todoist_mcp.server - DEBUG - Tool called: todoist_create_task
2025-11-28 10:15:32 - todoist_mcp.server - DEBUG - Arguments: {'content': 'Buy groceries', 'priority': 4}
2025-11-28 10:15:32 - todoist_mcp.server - DEBUG - Validation passed
2025-11-28 10:15:32 - todoist_mcp.server - DEBUG - API request successful
2025-11-28 10:15:32 - todoist_mcp.server - INFO - Task created: Buy groceries (ID: 1234567890)
```

**Log Output Location:**

- Logs are written to **stderr** (stdout is reserved for MCP protocol)
- When using Claude Desktop, check the application logs
- When running manually, logs appear in your terminal

**See:** `README.md` for more logging examples

### Testing with MCP Inspector

The MCP Inspector allows you to test the server interactively without Claude Desktop.

**Installation:**

```bash
# No installation needed - use npx
npx @modelcontextprotocol/inspector uv run python -m todoist_mcp.server
```

**Usage:**

1. Run the command above
2. Open the URL shown in your browser (usually `http://localhost:5173`)
3. You'll see:
   - List of available tools
   - Tool schemas and parameters
   - Interactive testing interface

**Testing a Tool:**

1. Select a tool (e.g., `todoist_get_tasks`)
2. Fill in parameters (if any)
3. Click "Run"
4. View the response

**Example:**

```text
Tool: todoist_create_task
Parameters:
  content: "Test task from Inspector"
  priority: 3

Response:
{
  "content": [
    {
      "type": "text",
      "text": "Task created successfully: Test task from Inspector (ID: 1234567890)"
    }
  ]
}
```

**Benefits:**

- Test tools without needing Claude Desktop
- See exact request/response format
- Verify tool parameters and schemas
- Debug tool issues quickly

**See:** [MCP Inspector Documentation](https://github.com/modelcontextprotocol/inspector)

### Manual Server Testing

Run the server directly to check for startup errors and environment issues.

**Basic Test:**

```bash
# Navigate to project directory
cd /path/to/todoist-mcp

# Run server with your API token
TODOIST_API_TOKEN=your_token uv run python -m todoist_mcp.server
```

**What to Look For:**

```text
# Successful startup - you'll see MCP protocol initialization
# Server is ready when you see JSON messages on stdout

# Errors will appear on stderr:
ERROR - Failed to load configuration
ERROR - TODOIST_API_TOKEN not found
```

**With Debug Logging:**

```bash
LOG_LEVEL=DEBUG TODOIST_API_TOKEN=your_token uv run python -m todoist_mcp.server
```

**Check Environment Variables:**

```bash
# Verify token is set
echo $TODOIST_API_TOKEN

# Run server
TODOIST_API_TOKEN=your_token uv run python -m todoist_mcp.server
```

**Common Issues:**

- **Server exits immediately:** Missing API token or import error
- **No output:** Server is waiting for MCP protocol input (this is normal)
- **Error messages:** Check stderr for details

**Stopping the Server:**

Press `Ctrl+C` to stop the server.

### Running Unit Tests

Unit tests verify the server logic without making real API calls.

**Run All Tests:**

```bash
pytest tests/test_server.py -v
```

**Run Specific Test:**

```bash
# Test validation functions
pytest tests/test_server.py::test_validate_task_id -v
pytest tests/test_server.py::test_validate_priority -v
```

**Run with Coverage:**

```bash
pytest --cov=src/todoist_mcp --cov-report=html tests/test_server.py
# Open htmlcov/index.html to view coverage report
```

**Integration Tests:**

For integration tests that use the real Todoist API, see `docs/integration-testing.md`.

**Quick Validation:**

```bash
# Run a quick smoke test
pytest tests/test_server.py -k "test_validate" -v
```

**What Tests Check:**

- Input validation (task IDs, priorities, labels)
- Error handling and messages
- Rate limit detection
- Configuration loading

**See:** `docs/integration-testing.md` for integration testing guide

### Verifying API Token Manually

Test your API token directly with the Todoist API to rule out token issues.

**Using curl:**

```bash
# Set your token (or use the one from .env)
export TODOIST_API_TOKEN=your_token_here

# Test token by getting projects
curl -H "Authorization: Bearer $TODOIST_API_TOKEN" \
     https://api.todoist.com/rest/v2/projects

# Should return JSON array of projects
```

**Expected Success Response:**

```json
[
  {
    "id": "1234567890",
    "name": "Inbox",
    "color": "grey",
    "is_favorite": false
  }
]
```

**Error Responses:**

```json
// 401 Unauthorized - Invalid token
{
  "error": "Unauthorized"
}

// 403 Forbidden - Token lacks permissions
{
  "error": "Forbidden"
}
```

**Testing Other Endpoints:**

```bash
# Get all tasks
curl -H "Authorization: Bearer $TODOIST_API_TOKEN" \
     https://api.todoist.com/rest/v2/tasks

# Get labels
curl -H "Authorization: Bearer $TODOIST_API_TOKEN" \
     https://api.todoist.com/rest/v2/labels
```

**Using Python:**

```python
from todoist_api_python.api import TodoistAPI

api = TodoistAPI("your_token_here")

try:
    projects = api.get_projects()
    print(f"Token is valid! Found {len(projects)} projects")
except Exception as e:
    print(f"Token error: {e}")
```

**See:** [Todoist REST API Documentation](https://developer.todoist.com/rest/v2/)

## FAQ

### Q: How do I know if my API token is working?

**A:** Run the server with DEBUG logging and check startup logs, or use curl to test the token directly:

```bash
LOG_LEVEL=DEBUG TODOIST_API_TOKEN=your_token uv run python -m todoist_mcp.server
# Look for "Configuration loaded" message

# Or test with curl:
curl -H "Authorization: Bearer $TODOIST_API_TOKEN" \
     https://api.todoist.com/rest/v2/projects
```

See [Verifying API Token Manually](#verifying-api-token-manually) for details.

### Q: Can I use this with my personal Todoist account?

**A:** Yes, but it's recommended to use a dedicated test account for integration tests to avoid mixing test data with your real tasks. The server works with any Todoist account (free or paid).

For integration testing, see `docs/integration-testing.md` for best practices.

### Q: Why aren't my tasks showing up?

**A:** Check these common causes:

1. **Project filter:** If you specified a `project_id`, tasks in other projects won't appear
2. **Tasks don't exist:** Verify tasks exist in Todoist web app
3. **Rate limit:** You may have hit the rate limit (wait 15 minutes)
4. **API token:** Token may be invalid or expired
5. **Completed tasks:** By default, only active tasks are returned

**Solution:**

```text
# In Claude Desktop:
"Show me all my Todoist tasks"

# Check without filters first, then add project_id if needed
```

### Q: How do I find task IDs?

**A:** Use the `todoist_get_tasks` tool first to list all tasks with their IDs:

```text
# In Claude Desktop:
"Show me all my Todoist tasks"

# Response will include task IDs:
- Task: Buy groceries (ID: 1234567890)
- Task: Finish report (ID: 9876543210)

# Then use the ID for other operations:
"Update task 1234567890 to set priority to 4"
```

Task IDs are unique identifiers assigned by Todoist when tasks are created.

### Q: What's the difference between unit and integration tests?

**A:**

- **Unit Tests** (`tests/test_server.py`):
  - Use mocks - no real API calls
  - Fast and safe to run anytime
  - Test validation, error handling, business logic
  - Don't require API token
  - Run with: `pytest tests/test_server.py`

- **Integration Tests** (`tests/integration/test_integration.py`):
  - Use real Todoist API
  - Require valid API token
  - Create/modify/delete real tasks
  - Test end-to-end functionality
  - Should use test account
  - Run with: `pytest tests/integration/`

**When to use each:**

- **Unit tests:** Quick validation during development, CI/CD pipelines
- **Integration tests:** Before releases, verifying API compatibility

See `docs/integration-testing.md` for comprehensive integration testing guide.

### Q: Is my API token safe?

**A:** Yes, if you follow security best practices:

**✅ Safe:**

- Store token in `.env` file (which is gitignored)
- Use environment variables in MCP config
- Server never logs the actual token value
- Logs use `[REDACTED]` for sensitive data

**❌ Unsafe:**

- Committing `.env` file to git
- Sharing your token publicly
- Using token in code comments
- Committing MCP config with token to public repo

**Security Features:**

- `.env` is in `.gitignore` by default
- Server logs redact sensitive information
- Token is only used for HTTPS API calls to Todoist
- Token is stored in environment variables, not in code

**If token is compromised:**

1. Revoke the token in [Todoist Settings](https://todoist.com/prefs/integrations)
2. Generate a new token
3. Update your `.env` file or MCP config
4. Restart the server

### Q: Where can I find more help?

**A:** Resources in order of detail:

1. **This troubleshooting guide** - Common issues and solutions
2. **API Documentation** - `docs/api.md` - Detailed tool documentation
3. **Integration Testing Guide** - `docs/integration-testing.md` - Testing setup and issues
4. **README** - Installation and usage instructions
5. **GitHub Issues** - [Report bugs or ask questions](https://github.com/denhamparry/todoist-mcp/issues)
6. **Todoist API Docs** - [Official API documentation](https://developer.todoist.com/rest/v2/)
7. **MCP Documentation** - [Model Context Protocol specification](https://modelcontextprotocol.io/)

**Before opening an issue:**

- Check this troubleshooting guide
- Search existing GitHub issues
- Include debug logs (`LOG_LEVEL=DEBUG`)
- Specify your environment (OS, Python version, uv version)

## See Also

- **[API Documentation](api.md)** - Detailed tool documentation, error handling, rate limits
- **[Integration Testing Guide](integration-testing.md)** - Integration test setup and troubleshooting
- **[README](../README.md)** - Installation, configuration, and usage
- **[Todoist REST API](https://developer.todoist.com/rest/v2/)** - Official Todoist API documentation
- **[Todoist API Token Guide](https://todoist.com/help/articles/find-your-api-token-Jpzx9IIlB)** - How to find your API token
- **[MCP Inspector](https://github.com/modelcontextprotocol/inspector)** - Interactive testing tool
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - MCP specification

## Getting Help

If you've tried the troubleshooting steps and still have issues:

1. **Search existing issues:** [GitHub Issues](https://github.com/denhamparry/todoist-mcp/issues)
2. **Open a new issue:** Include:
   - Clear description of the problem
   - Steps to reproduce
   - Debug logs (`LOG_LEVEL=DEBUG`)
   - Your environment:
     - OS and version
     - Python version (`python --version`)
     - uv version (`uv --version`)
     - Todoist plan (free/pro)
   - Relevant configuration (redact your API token!)

**Example Issue:**

```markdown
## Problem

Server crashes when creating tasks with priorities

## Steps to Reproduce

1. Run server with DEBUG logging
2. Create task with priority 4
3. Server exits with error

## Debug Logs

ERROR - Priority validation failed

## Environment

- OS: macOS 15.1
- Python: 3.12.0
- uv: 0.5.11
- Todoist: Free plan
```

**Response Time:**

- Issues are typically reviewed within 1-2 business days
- For urgent production issues, include `[URGENT]` in the title

**Contributing:**

Found a fix? Pull requests are welcome! See `CONTRIBUTING.md` for guidelines.
