# Integration Testing Guide

This guide explains how to set up, run, and safely use integration tests that
interact with the real Todoist API.

## Overview

Integration tests in this project make real API calls to Todoist to verify
end-to-end functionality. Unlike unit tests (which use mocks), integration tests
ensure our MCP server correctly interacts with the actual Todoist API.

**When to run integration tests:**

- Before major releases
- After significant API-related changes
- When troubleshooting API integration issues
- As part of manual testing before merging critical PRs

**Why not in CI/CD?**

- Require real Todoist credentials
- Create actual API load and quota usage
- Need dedicated test accounts to avoid data conflicts

## Prerequisites

1. **Todoist account** (free or paid)
2. **Dedicated test account recommended** - Don't use your personal account
3. **API token access** - Available in Todoist settings

## Getting Your API Token

1. Log in to your Todoist test account at <https://todoist.com>
2. Navigate to **Settings** → **Integrations** → **Developer**
3. Copy your **API token** (it will look like a long string of random
   characters)
4. Keep this token secure - treat it like a password

**Official guide:**
<https://todoist.com/help/articles/find-your-api-token-Jpzx9IIlB>

**Security best practices:**

- Never commit tokens to version control
- Use `.env` file (which is gitignored)
- Use a dedicated test account, not your personal account
- Regenerate token if accidentally exposed

## Creating a Test Project

To isolate integration tests and prevent accidental modification of real data:

1. In your Todoist test account, create a new project
2. Name it something obvious like "MCP Integration Tests" or "API Test Project"
3. Get the project ID:
   - Open the project in Todoist
   - Check the URL: `https://todoist.com/app/project/1234567890`
   - The number at the end is your project ID
4. Use this project ID in your `.env` file

**Why use a dedicated test project?**

- Tests create and delete real tasks
- Isolates test data from personal/production data
- Makes cleanup easier if tests fail
- Allows running tests without affecting real work

## Environment Setup

Create a `.env` file in the project root (copy from `.env.example`):

```bash
# Required for integration tests
TODOIST_API_TOKEN=your_real_token_here

# Optional: Isolate tests to specific project
# Highly recommended for safety
TODOIST_TEST_PROJECT_ID=1234567890

# Optional: Logging level
LOG_LEVEL=INFO
```

**Verification:**

```bash
# Ensure .env is gitignored
git check-ignore .env  # Should output: .env

# Verify token is set
grep TODOIST_API_TOKEN .env
```

## Safety Guidelines

⚠️ **CRITICAL SAFETY WARNINGS:**

- **Use a dedicated test account** - Not your personal Todoist account
- **Use a specific test project** - Set `TODOIST_TEST_PROJECT_ID`
- **Tests create and delete real data** - They make actual API calls
- **Don't run against production projects** - Data will be modified

✅ **Good news:**

- Tests clean up after themselves (delete created tasks)
- Tests are marked with `@pytest.mark.integration` for selective running
- Tests skip automatically if credentials aren't configured

## Running Integration Tests

**Run all integration tests:**

```bash
pytest tests/test_integration.py -m integration -v
```

**Run a specific test:**

```bash
pytest tests/test_integration.py::test_create_and_delete_task_workflow -v
```

**Run with coverage:**

```bash
pytest tests/test_integration.py -m integration --cov=src/todoist_mcp --cov-report=html
```

**Run both unit and integration tests:**

```bash
pytest -v
```

**List available integration tests:**

```bash
pytest tests/test_integration.py -m integration --collect-only
```

## What's Tested

The integration test suite covers:

### Task Operations

- **Creating tasks** - With various parameters (content, description, due dates)
- **Retrieving tasks** - Get all tasks, filter by project
- **Updating tasks** - Modify content, descriptions, due dates
- **Completing tasks** - Mark tasks as complete
- **Deleting tasks** - Remove tasks and verify deletion

### Project Operations

- **Getting projects** - Retrieve all projects
- **Project filtering** - Filter tasks by project ID

### Label Operations

- **Getting labels** - Retrieve all available labels

### Due Date Handling

- **Natural language dates** - "tomorrow", "next Monday"
- **Specific dates** - ISO format dates
- **Date parsing** - Verify due date structure

## Troubleshooting

### Error: `TODOIST_API_TOKEN not set - skipping integration tests`

**Cause:** Environment variable `TODOIST_API_TOKEN` is not configured.

**Solution:**

1. Create `.env` file in project root
2. Add `TODOIST_API_TOKEN=your_token_here`
3. Verify file is loaded: `grep TODOIST_API_TOKEN .env`

### Error: `401 Unauthorized`

**Cause:** API token is invalid, expired, or incorrect.

**Solution:**

1. Verify token in `.env` file is correct (no extra spaces)
2. Log in to Todoist and check token is still active
3. Regenerate token in Todoist settings if needed
4. Update `.env` file with new token

### Error: `404 Not Found` or `403 Forbidden`

**Cause:** Project ID doesn't exist or you don't have access.

**Solution:**

1. Verify `TODOIST_TEST_PROJECT_ID` matches a real project
2. Check you're using the test account's project
3. Ensure project wasn't deleted
4. Try removing `TODOIST_TEST_PROJECT_ID` to test without project isolation

### Error: `429 Too Many Requests`

**Cause:** Rate limit exceeded (too many API calls in short time).

**Solution:**

1. Wait a few minutes before retrying
2. Reduce test frequency
3. Check Todoist API quota limits for your account tier

### Tests pass but create duplicate tasks

**Cause:** Test cleanup failed in previous run.

**Solution:**

1. Manually delete test tasks in Todoist
2. Check test project for leftover data
3. Re-run tests - they should clean up properly

### Import errors or module not found

**Cause:** Dependencies not installed or virtual environment not activated.

**Solution:**

```bash
# Using uv (recommended)
uv pip install -e ".[dev]"

# Using pip
pip install -e ".[dev]"
```

## Example Output

**Successful test run:**

```text
$ pytest tests/test_integration.py -m integration -v

======================== test session starts =========================
platform darwin -- Python 3.12.0, pytest-7.4.3, pluggy-1.3.0
cachedir: .pytest_cache
rootdir: /path/to/todoist-mcp
plugins: cov-4.1.0, asyncio-0.21.1
collected 12 items / 0 deselected / 12 selected

tests/test_integration.py::test_get_tasks PASSED               [  8%]
tests/test_integration.py::test_get_projects PASSED            [ 16%]
tests/test_integration.py::test_get_labels PASSED              [ 25%]
tests/test_integration.py::test_create_and_delete_task_workflow PASSED [ 33%]
tests/test_integration.py::test_update_task PASSED             [ 41%]
tests/test_integration.py::test_complete_task PASSED           [ 50%]
tests/test_integration.py::test_create_task_with_due_date PASSED [ 58%]
tests/test_integration.py::test_create_task_with_project PASSED [ 66%]
tests/test_integration.py::test_filter_tasks_by_project PASSED [ 75%]
tests/test_integration.py::test_create_task_with_description PASSED [ 83%]
tests/test_integration.py::test_update_task_due_date PASSED    [ 91%]
tests/test_integration.py::test_task_cleanup PASSED            [100%]

======================== 12 passed in 8.42s =========================
```

**Test skipped (no credentials):**

```text
$ pytest tests/test_integration.py -m integration -v

tests/test_integration.py::test_get_tasks SKIPPED (TODOIST_API_TOKEN not set)
tests/test_integration.py::test_get_projects SKIPPED (TODOIST_API_TOKEN not set)
...
======================== 12 skipped in 0.12s ========================
```

## CI/CD Considerations

Integration tests are **not run in CI/CD** for the following reasons:

1. **Credentials** - Require real Todoist API tokens
2. **API load** - Create actual API requests and quota usage
3. **Data isolation** - Need dedicated test accounts to avoid conflicts
4. **Cost** - May incur API quota or rate limit issues
5. **Reliability** - Dependent on external service availability

**When to run:**

- Manually before major releases
- As part of pre-release validation
- When investigating API-related bugs
- During local development and testing

## Best Practices

### Do's ✅

- **Use dedicated test account** - Separate from personal Todoist
- **Use test project isolation** - Set `TODOIST_TEST_PROJECT_ID`
- **Run before releases** - Manual validation of API integration
- **Keep test data minimal** - Only create necessary test tasks
- **Monitor API quota** - Be aware of rate limits
- **Clean up manually if tests fail** - Check test project for leftover tasks

### Don'ts ❌

- **Don't use personal account** - Risk modifying real data
- **Don't run in CI without isolation** - Can't share credentials safely
- **Don't commit `.env` file** - Contains sensitive tokens
- **Don't run tests too frequently** - Respect API rate limits
- **Don't ignore cleanup failures** - Manually remove test data
- **Don't hardcode tokens** - Always use environment variables

## Advanced Usage

### Running specific test categories

```bash
# Only task operations
pytest tests/test_integration.py -k "task" -v

# Only project-related tests
pytest tests/test_integration.py -k "project" -v

# Exclude specific tests
pytest tests/test_integration.py -k "not update" -v
```

### Debugging failed tests

```bash
# Show detailed output
pytest tests/test_integration.py -vv

# Drop into debugger on failure
pytest tests/test_integration.py --pdb

# Show print statements
pytest tests/test_integration.py -s
```

### Test coverage analysis

```bash
# Generate HTML coverage report
pytest tests/test_integration.py -m integration --cov=src/todoist_mcp --cov-report=html

# Open coverage report
open htmlcov/index.html
```

## Related Documentation

- [Todoist API Documentation](https://developer.todoist.com/rest/v2/)
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [API Token Guide](https://todoist.com/help/articles/find-your-api-token-Jpzx9IIlB)

## Support

If you encounter issues not covered in this guide:

1. Check the [Todoist API
   Documentation](https://developer.todoist.com/rest/v2/)
2. Review test code in `tests/test_integration.py`
3. Check `tests/conftest.py` for fixture configuration
4. Open an issue on GitHub with details about the problem
