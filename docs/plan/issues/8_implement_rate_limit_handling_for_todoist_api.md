# GitHub Issue #8: Implement rate limit handling for Todoist API

**Issue:** [#8](https://github.com/denhamparry/todoist-mcp/issues/8)
**Status:** Complete
**Priority:** Nice to have - Future improvement
**Date:** 2025-11-27

## Problem Statement

The Todoist API has rate limits (~450 requests per 15 minutes for standard plans, higher for premium plans). Currently, the server does not handle rate limit errors gracefully, which can result in:

1. Unclear error messages when rate limits are exceeded
2. No automatic retry logic
3. Poor user experience during high-usage scenarios
4. No visibility into rate limit events for monitoring

### Current Behavior

When a rate limit (HTTP 429) is hit:

- Generic exception is caught and returned as `"Error fetching tasks: {str(e)}"`
- No specific detection or handling of 429 errors
- No retry logic with exponential backoff
- Rate limit events are not specifically logged
- Users receive unclear error messages

### Expected Behavior

When rate limits are exceeded:

- Clear, user-friendly error messages explaining the rate limit
- Optional retry logic with exponential backoff
- Rate limit events logged for monitoring
- Users know to wait before retrying
- Documentation updated with rate limit information

## Current State Analysis

### Relevant Code/Config

**src/todoist_mcp/server.py** - All API tool functions have generic error handling:

```python
except Exception as e:
    logger.error(
        f"Failed to get tasks - project_id={project_id!r} label={label!r} "
        f"error={str(e)}",
        exc_info=True,
    )
    return f"Error fetching tasks: {str(e)}"
```

Current error handling (lines 192-198, 258-263, 321-326, 355-360, 389-394, 426-428, 458-460):

- Generic `Exception` catch-all
- No specific rate limit detection
- No retry logic
- Logs errors but doesn't distinguish rate limit errors

**docs/api.md** - Documentation mentions rate limits (line 323-329):

- States standard plans have ~450 requests per 15 minutes
- Mentions premium plans have higher limits
- Says "server handles rate limiting automatically" (currently false)
- Lists rate limiting as a common error scenario

**tests/test_server.py** - No tests for rate limit handling:

- No test cases for 429 errors
- No validation of rate limit error messages
- No tests for retry logic

### Related Context

**Todoist API Rate Limit Details:**

- Standard plans: ~450 requests per 15 minutes
- Premium plans: Higher limits
- Response headers include:
  - `X-RateLimit-Limit` - Maximum requests allowed
  - `X-RateLimit-Remaining` - Requests remaining in current window
  - `Retry-After` - Seconds to wait before retrying (on 429 responses)

**todoist-api-python Library:**

- Does not have built-in automatic backoff for rate limits ([GitHub Issue #38](https://github.com/Doist/todoist-api-python/issues/38))
- Raises exceptions on API errors (including 429)
- Exception likely contains response object with status code and headers

## Solution Design

### Approach

Implement a multi-layered approach to rate limit handling:

1. **Detection Layer**: Detect rate limit errors specifically (HTTP 429)
2. **User Feedback Layer**: Return clear, actionable error messages
3. **Retry Layer (Optional)**: Add configurable retry logic with exponential backoff
4. **Logging Layer**: Log rate limit events for monitoring
5. **Documentation Layer**: Update documentation with rate limit information

**Rationale:**

- Layered approach allows gradual implementation and testing
- User-friendly messages improve UX immediately (low effort, high value)
- Optional retry logic provides flexibility (can be enabled/disabled)
- Logging enables monitoring and debugging
- Documentation helps users understand and avoid rate limits

**Trade-offs Considered:**

- **Automatic retry vs. immediate error**: Chose configurable retry to give users control
- **Retry count**: Start conservative (2-3 retries) to avoid long wait times
- **Exponential backoff vs. fixed delay**: Chose exponential to reduce server load
- **Global retry config vs. per-tool**: Global is simpler and more consistent

### Implementation

**1. Add Rate Limit Detection Helper**

Create a helper function to detect rate limit errors:

```python
def is_rate_limit_error(error: Exception) -> bool:
    """Check if an exception is a rate limit error (HTTP 429).

    Args:
        error: Exception to check

    Returns:
        True if rate limit error, False otherwise
    """
    error_str = str(error).lower()
    # Check for common rate limit indicators
    return (
        "429" in str(error) or
        "rate limit" in error_str or
        "too many requests" in error_str
    )
```

**2. Add Retry Helper with Exponential Backoff**

Create a retry decorator/helper:

```python
import asyncio
from typing import Optional

async def retry_with_backoff(
    func,
    max_retries: int = 3,
    base_delay: float = 2.0,
    *args,
    **kwargs
):
    """Retry async function with exponential backoff on rate limit errors.

    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds (will be exponentially increased)
        *args, **kwargs: Arguments to pass to func

    Returns:
        Result from func

    Raises:
        Exception if max retries exceeded
    """
    for attempt in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if is_rate_limit_error(e) and attempt < max_retries:
                wait_time = base_delay * (2 ** attempt)
                logger.warning(
                    f"Rate limit hit (attempt {attempt + 1}/{max_retries + 1}), "
                    f"retrying in {wait_time}s"
                )
                await asyncio.sleep(wait_time)
            else:
                raise
```

**3. Update Error Handling in All Tools**

Modify exception handling to detect and report rate limits:

```python
except Exception as e:
    # Check for rate limit error
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

    logger.error(
        f"Failed to get tasks - project_id={project_id!r} label={label!r} "
        f"error={str(e)}",
        exc_info=True,
    )
    return f"Error fetching tasks: {str(e)}"
```

**4. Optional: Add Configuration for Retry Logic**

Add environment variable to enable/disable retry:

```python
# In server.py initialization section
ENABLE_RETRY = os.getenv("TODOIST_ENABLE_RETRY", "false").lower() == "true"
MAX_RETRIES = int(os.getenv("TODOIST_MAX_RETRIES", "3"))
```

Use in tool functions:

```python
try:
    if ENABLE_RETRY:
        tasks = await retry_with_backoff(
            todoist.get_tasks,
            max_retries=MAX_RETRIES,
            project_id=project_id,
            label=label
        )
    else:
        task_generator = await todoist.get_tasks(project_id=project_id, label=label)
        # ... existing code
```

### Benefits

1. **Immediate Value**: Clear error messages help users understand and resolve issues
2. **Resilience**: Optional retry logic reduces transient failures
3. **Visibility**: Logging enables monitoring and debugging
4. **Flexibility**: Configuration allows users to enable/disable retry
5. **User Experience**: Better feedback reduces frustration
6. **Future-Proof**: Foundation for more advanced rate limit handling

## Implementation Plan

### Step 1: Add Rate Limit Detection Helper

**File:** `src/todoist_mcp/server.py`

**Changes:**

- Add `is_rate_limit_error()` helper function after validation helpers (after line 130)

**Code:**

```python
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
        "429" in str(error) or
        "rate limit" in error_str or
        "too many requests" in error_str
    )
```

**Testing:**

```python
# In test file
def test_is_rate_limit_error_with_429():
    error = Exception("HTTP 429: Too Many Requests")
    assert is_rate_limit_error(error) is True

def test_is_rate_limit_error_with_rate_limit_text():
    error = Exception("Rate limit exceeded")
    assert is_rate_limit_error(error) is True

def test_is_rate_limit_error_with_other_error():
    error = Exception("Invalid token")
    assert is_rate_limit_error(error) is False
```

### Step 2: Update Error Handling in todoist_get_tasks

**File:** `src/todoist_mcp/server.py`

**Changes:**

- Update exception handling in `todoist_get_tasks` (lines 192-198)
- Add specific check for rate limit errors before generic error handling

**Code:**

```python
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
```

**Testing:**

```python
@pytest.mark.asyncio
async def test_todoist_get_tasks_rate_limit_error(mock_api_token, monkeypatch):
    """Test todoist_get_tasks with rate limit error (429)"""
    async def mock_get_tasks_rate_limited(**kwargs):
        raise Exception("HTTP 429: Too Many Requests")

    import todoist_mcp.server
    monkeypatch.setattr(
        todoist_mcp.server.todoist,
        "get_tasks",
        mock_get_tasks_rate_limited
    )

    from todoist_mcp.server import todoist_get_tasks
    result = await todoist_get_tasks()

    assert "rate limit exceeded" in result.lower()
    assert "wait a few minutes" in result.lower()
    assert "450 requests per 15 minutes" in result
```

### Step 3: Update Error Handling in All Other Tools

**File:** `src/todoist_mcp/server.py`

**Changes:**

- Update exception handling in all remaining tool functions:
  - `todoist_create_task` (lines 258-263)
  - `todoist_update_task` (lines 321-326)
  - `todoist_complete_task` (lines 355-360)
  - `todoist_delete_task` (lines 389-394)
  - `todoist_get_projects` (lines 426-428)
  - `todoist_get_labels` (lines 458-460)

**Code Pattern (same for all tools):**

```python
except Exception as e:
    # Check for rate limit error
    if is_rate_limit_error(e):
        logger.warning(
            f"Rate limit exceeded - tool=todoist_create_task "
            f"content={content!r}"  # Add relevant parameters
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
```

**Testing:**

Add rate limit test for each tool:

```python
@pytest.mark.asyncio
async def test_todoist_create_task_rate_limit(mock_api_token, monkeypatch):
    """Test todoist_create_task with rate limit error"""
    async def mock_rate_limit(**kwargs):
        raise Exception("429 Too Many Requests")

    import todoist_mcp.server
    monkeypatch.setattr(todoist_mcp.server.todoist, "add_task", mock_rate_limit)

    from todoist_mcp.server import todoist_create_task
    result = await todoist_create_task(content="Test")

    assert "rate limit exceeded" in result.lower()
    assert "wait a few minutes" in result.lower()

# Similar tests for update, complete, delete, get_projects, get_labels
```

### Step 4: Add Retry Logic Helper (Optional)

**File:** `src/todoist_mcp/server.py`

**Changes:**

- Add configuration for retry logic after imports (after line 26)
- Add `retry_with_backoff` helper function after `is_rate_limit_error`

**Configuration Code:**

```python
# Rate limit retry configuration
ENABLE_RETRY = os.getenv("TODOIST_ENABLE_RETRY", "false").lower() == "true"
MAX_RETRIES = int(os.getenv("TODOIST_MAX_RETRIES", "3"))
RETRY_BASE_DELAY = float(os.getenv("TODOIST_RETRY_BASE_DELAY", "2.0"))

logger.info(
    f"Rate limit retry: enabled={ENABLE_RETRY} max_retries={MAX_RETRIES} "
    f"base_delay={RETRY_BASE_DELAY}s"
)
```

**Helper Function Code:**

```python
async def retry_with_backoff(func, max_retries: int, base_delay: float, *args, **kwargs):
    """Retry async function with exponential backoff on rate limit errors.

    This helper implements exponential backoff for rate limit errors:
    - 1st retry: wait base_delay seconds (default: 2s)
    - 2nd retry: wait base_delay * 2 seconds (default: 4s)
    - 3rd retry: wait base_delay * 4 seconds (default: 8s)
    - etc.

    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds (will be exponentially increased)
        *args, **kwargs: Arguments to pass to func

    Returns:
        Result from func

    Raises:
        Exception if max retries exceeded or non-rate-limit error occurs
    """
    for attempt in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if is_rate_limit_error(e) and attempt < max_retries:
                wait_time = base_delay * (2 ** attempt)
                logger.warning(
                    f"Rate limit hit (attempt {attempt + 1}/{max_retries + 1}), "
                    f"retrying in {wait_time}s - error={str(e)}"
                )
                await asyncio.sleep(wait_time)
            else:
                # Re-raise if not rate limit error or max retries exceeded
                raise
```

**Testing:**

```python
@pytest.mark.asyncio
async def test_retry_with_backoff_success_after_retry(mock_api_token):
    """Test retry succeeds after rate limit error"""
    call_count = 0

    async def mock_func_that_fails_once():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise Exception("429 Too Many Requests")
        return "success"

    from todoist_mcp.server import retry_with_backoff
    result = await retry_with_backoff(mock_func_that_fails_once, max_retries=3, base_delay=0.1)

    assert result == "success"
    assert call_count == 2  # Failed once, succeeded on retry

@pytest.mark.asyncio
async def test_retry_with_backoff_exceeds_max_retries(mock_api_token):
    """Test retry fails after max retries exceeded"""
    async def mock_func_always_fails():
        raise Exception("429 Too Many Requests")

    from todoist_mcp.server import retry_with_backoff

    with pytest.raises(Exception, match="429"):
        await retry_with_backoff(mock_func_always_fails, max_retries=2, base_delay=0.1)

@pytest.mark.asyncio
async def test_retry_with_backoff_non_rate_limit_error(mock_api_token):
    """Test retry doesn't retry non-rate-limit errors"""
    call_count = 0

    async def mock_func_auth_error():
        nonlocal call_count
        call_count += 1
        raise Exception("401 Unauthorized")

    from todoist_mcp.server import retry_with_backoff

    with pytest.raises(Exception, match="401"):
        await retry_with_backoff(mock_func_auth_error, max_retries=3, base_delay=0.1)

    assert call_count == 1  # Should not retry non-rate-limit errors
```

### Step 5: Update Documentation

**File:** `docs/api.md`

**Changes:**

- Update rate limits section (lines 323-329) to reflect actual implementation
- Add section about rate limit error handling
- Document retry configuration options

**Updated Content:**

```markdown
## Rate Limits

Todoist API has rate limits that vary by plan:

- **Standard plans**: ~450 requests per 15 minutes
- **Premium plans**: Higher limits

The server includes rate limit response headers:
- `X-RateLimit-Limit` - Maximum requests allowed
- `X-RateLimit-Remaining` - Requests remaining in current window
- `Retry-After` - Seconds to wait before retrying (on 429 responses)

### Rate Limit Handling

When rate limits are exceeded, the server will:

1. **Detect** HTTP 429 errors automatically
2. **Return** clear error message:

   ```text
   Error: Todoist API rate limit exceeded.
   Please wait a few minutes and try again.
   (Standard plans: ~450 requests per 15 minutes)
   ```

3. **Log** rate limit events for monitoring
4. **Optionally retry** with exponential backoff (if enabled)

### Enabling Automatic Retry (Optional)

To enable automatic retry with exponential backoff, set these environment variables:

```bash
# Enable retry on rate limit errors
TODOIST_ENABLE_RETRY=true

# Maximum number of retry attempts (default: 3)
TODOIST_MAX_RETRIES=3

# Base delay in seconds for exponential backoff (default: 2.0)
# Delays: 2s, 4s, 8s, 16s, etc.
TODOIST_RETRY_BASE_DELAY=2.0
```

**MCP Configuration:**

```json
{
  "mcpServers": {
    "todoist": {
      "command": "uv",
      "args": ["run", "todoist-mcp"],
      "env": {
        "TODOIST_API_TOKEN": "your_token_here",
        "TODOIST_ENABLE_RETRY": "true",
        "TODOIST_MAX_RETRIES": "3"
      }
    }
  }
}
```

### Best Practices for Rate Limits

1. **Cache results** when possible to reduce API calls
2. **Batch operations** instead of individual calls
3. **Monitor rate limit headers** to track usage
4. **Enable retry logic** for production use
5. **Space out requests** to avoid hitting limits

**File:** `README.md`

**Changes:**

- Add note about rate limit handling in Features section (after line 13)

**Code:**

```markdown
## Features

- Create, read, update, and delete tasks
- Manage projects and labels
- Natural language due dates (e.g., "tomorrow", "next Monday at 3pm")
- Priority and label support
- Complete task workflow integration
- **Rate limit handling** with clear error messages and optional retry logic
```

### Step 6: Add Comprehensive Tests

**File:** `tests/test_server.py`

**Changes:**

- Add test section for rate limit handling (after line 757)

**Code:**

```python
# Rate limit handling tests


@pytest.mark.asyncio
async def test_is_rate_limit_error_with_429(mock_api_token):
    """Test is_rate_limit_error detects 429 status code"""
    from todoist_mcp.server import is_rate_limit_error

    error = Exception("HTTP 429: Too Many Requests")
    assert is_rate_limit_error(error) is True


@pytest.mark.asyncio
async def test_is_rate_limit_error_with_rate_limit_text(mock_api_token):
    """Test is_rate_limit_error detects 'rate limit' keyword"""
    from todoist_mcp.server import is_rate_limit_error

    error = Exception("Rate limit exceeded, please try again later")
    assert is_rate_limit_error(error) is True


@pytest.mark.asyncio
async def test_is_rate_limit_error_with_too_many_requests(mock_api_token):
    """Test is_rate_limit_error detects 'too many requests' keyword"""
    from todoist_mcp.server import is_rate_limit_error

    error = Exception("Too many requests")
    assert is_rate_limit_error(error) is True


@pytest.mark.asyncio
async def test_is_rate_limit_error_with_other_error(mock_api_token):
    """Test is_rate_limit_error returns False for non-rate-limit errors"""
    from todoist_mcp.server import is_rate_limit_error

    error = Exception("Invalid API token")
    assert is_rate_limit_error(error) is False


@pytest.mark.asyncio
async def test_todoist_get_tasks_rate_limit_error(mock_api_token, monkeypatch):
    """Test todoist_get_tasks handles rate limit error with helpful message"""
    async def mock_get_tasks_rate_limited(**kwargs):
        raise Exception("HTTP 429: Too Many Requests")

    import todoist_mcp.server
    monkeypatch.setattr(
        todoist_mcp.server.todoist,
        "get_tasks",
        mock_get_tasks_rate_limited
    )

    from todoist_mcp.server import todoist_get_tasks
    result = await todoist_get_tasks()

    assert "rate limit exceeded" in result.lower()
    assert "wait a few minutes" in result.lower()
    assert "450 requests per 15 minutes" in result


@pytest.mark.asyncio
async def test_todoist_create_task_rate_limit_error(mock_api_token, monkeypatch):
    """Test todoist_create_task handles rate limit error"""
    async def mock_rate_limit(**kwargs):
        raise Exception("429 Too Many Requests")

    import todoist_mcp.server
    monkeypatch.setattr(todoist_mcp.server.todoist, "add_task", mock_rate_limit)

    from todoist_mcp.server import todoist_create_task
    result = await todoist_create_task(content="Test")

    assert "rate limit exceeded" in result.lower()
    assert "wait a few minutes" in result.lower()


@pytest.mark.asyncio
async def test_todoist_update_task_rate_limit_error(mock_api_token, monkeypatch):
    """Test todoist_update_task handles rate limit error"""
    async def mock_rate_limit(**kwargs):
        raise Exception("Rate limit exceeded")

    import todoist_mcp.server
    monkeypatch.setattr(todoist_mcp.server.todoist, "update_task", mock_rate_limit)

    from todoist_mcp.server import todoist_update_task
    result = await todoist_update_task(task_id="12345", content="Updated")

    assert "rate limit exceeded" in result.lower()


@pytest.mark.asyncio
async def test_todoist_complete_task_rate_limit_error(mock_api_token, monkeypatch):
    """Test todoist_complete_task handles rate limit error"""
    async def mock_rate_limit(**kwargs):
        raise Exception("Too Many Requests")

    import todoist_mcp.server
    monkeypatch.setattr(todoist_mcp.server.todoist, "complete_task", mock_rate_limit)

    from todoist_mcp.server import todoist_complete_task
    result = await todoist_complete_task(task_id="12345")

    assert "rate limit exceeded" in result.lower()


@pytest.mark.asyncio
async def test_todoist_delete_task_rate_limit_error(mock_api_token, monkeypatch):
    """Test todoist_delete_task handles rate limit error"""
    async def mock_rate_limit(**kwargs):
        raise Exception("HTTP 429")

    import todoist_mcp.server
    monkeypatch.setattr(todoist_mcp.server.todoist, "delete_task", mock_rate_limit)

    from todoist_mcp.server import todoist_delete_task
    result = await todoist_delete_task(task_id="12345")

    assert "rate limit exceeded" in result.lower()


@pytest.mark.asyncio
async def test_todoist_get_projects_rate_limit_error(mock_api_token, monkeypatch):
    """Test todoist_get_projects handles rate limit error"""
    async def mock_rate_limit(**kwargs):
        raise Exception("429: Rate limit exceeded")

    import todoist_mcp.server
    monkeypatch.setattr(todoist_mcp.server.todoist, "get_projects", mock_rate_limit)

    from todoist_mcp.server import todoist_get_projects
    result = await todoist_get_projects()

    assert "rate limit exceeded" in result.lower()


@pytest.mark.asyncio
async def test_todoist_get_labels_rate_limit_error(mock_api_token, monkeypatch):
    """Test todoist_get_labels handles rate limit error"""
    async def mock_rate_limit(**kwargs):
        raise Exception("rate limit exceeded")

    import todoist_mcp.server
    monkeypatch.setattr(todoist_mcp.server.todoist, "get_labels", mock_rate_limit)

    from todoist_mcp.server import todoist_get_labels
    result = await todoist_get_labels()

    assert "rate limit exceeded" in result.lower()


@pytest.mark.asyncio
async def test_rate_limit_error_logs_warning(mock_api_token, monkeypatch, caplog):
    """Test that rate limit errors log at WARNING level"""
    async def mock_rate_limit(**kwargs):
        raise Exception("429 Too Many Requests")

    import todoist_mcp.server
    import logging
    monkeypatch.setattr(todoist_mcp.server.todoist, "get_tasks", mock_rate_limit)

    from todoist_mcp.server import todoist_get_tasks

    with caplog.at_level(logging.WARNING):
        await todoist_get_tasks()

        # Verify warning logged for rate limit
        assert "Rate limit exceeded" in caplog.text
        assert "todoist_get_tasks" in caplog.text


# Optional retry logic tests (Step 4)


@pytest.mark.asyncio
async def test_retry_with_backoff_success_after_retry(mock_api_token):
    """Test retry succeeds after rate limit error"""
    call_count = 0

    async def mock_func_that_fails_once():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise Exception("429 Too Many Requests")
        return "success"

    from todoist_mcp.server import retry_with_backoff
    result = await retry_with_backoff(
        mock_func_that_fails_once,
        max_retries=3,
        base_delay=0.1
    )

    assert result == "success"
    assert call_count == 2  # Failed once, succeeded on retry


@pytest.mark.asyncio
async def test_retry_with_backoff_exceeds_max_retries(mock_api_token):
    """Test retry fails after max retries exceeded"""
    async def mock_func_always_fails():
        raise Exception("429 Too Many Requests")

    from todoist_mcp.server import retry_with_backoff

    with pytest.raises(Exception, match="429"):
        await retry_with_backoff(
            mock_func_always_fails,
            max_retries=2,
            base_delay=0.1
        )


@pytest.mark.asyncio
async def test_retry_with_backoff_non_rate_limit_error(mock_api_token):
    """Test retry doesn't retry non-rate-limit errors"""
    call_count = 0

    async def mock_func_auth_error():
        nonlocal call_count
        call_count += 1
        raise Exception("401 Unauthorized")

    from todoist_mcp.server import retry_with_backoff

    with pytest.raises(Exception, match="401"):
        await retry_with_backoff(
            mock_func_auth_error,
            max_retries=3,
            base_delay=0.1
        )

    assert call_count == 1  # Should not retry non-rate-limit errors


@pytest.mark.asyncio
async def test_retry_with_backoff_exponential_delay(mock_api_token, monkeypatch):
    """Test retry uses exponential backoff delays"""
    import asyncio
    import time

    delays = []
    original_sleep = asyncio.sleep

    async def mock_sleep(delay):
        delays.append(delay)
        await original_sleep(0)  # Don't actually wait in test

    monkeypatch.setattr(asyncio, "sleep", mock_sleep)

    call_count = 0
    async def mock_func_fails_three_times():
        nonlocal call_count
        call_count += 1
        if call_count <= 3:
            raise Exception("Rate limit exceeded")
        return "success"

    from todoist_mcp.server import retry_with_backoff
    await retry_with_backoff(
        mock_func_fails_three_times,
        max_retries=3,
        base_delay=2.0
    )

    # Verify exponential backoff: 2s, 4s, 8s
    assert delays == [2.0, 4.0, 8.0]
```

## Testing Strategy

### Unit Testing

**Rate Limit Detection Tests:**

1. Test `is_rate_limit_error()` with various error formats:
   - "429" in error message
   - "rate limit" keyword
   - "too many requests" keyword
   - Non-rate-limit errors return False

**Error Handling Tests:**

2. Test each tool function with rate limit error:

- Mock API to raise 429 error
- Verify clear error message returned
- Verify "wait a few minutes" guidance included
- Verify rate limit info (450 requests) included

**Logging Tests:**

3. Test rate limit errors log at WARNING level:

- Verify warning message logged
- Verify tool name included in log
- Verify parameters included in log

**Retry Logic Tests (Optional):**

4. Test `retry_with_backoff()` helper:

- Succeeds after transient rate limit error
- Fails after max retries exceeded
- Doesn't retry non-rate-limit errors
- Uses exponential backoff (2s, 4s, 8s, etc.)

### Integration Testing

**Manual Testing:**

1. Test with actual Todoist API:
   - Make rapid requests to trigger rate limit
   - Verify error message clarity
   - Verify retry logic (if enabled)
   - Check logs for rate limit events

**Performance Testing:**
2. Test retry delays don't block other operations
3. Verify exponential backoff reduces server load

### Regression Testing

**Existing Functionality:**

1. Run full test suite to ensure no regressions
2. Verify all existing tools still work correctly
3. Verify error handling for non-rate-limit errors unchanged

## Success Criteria

- [x] Rate limit errors (HTTP 429) are detected specifically
- [x] Users receive clear, actionable error messages when rate limited
- [x] Error messages explain the rate limit (~450 requests per 15 minutes)
- [x] Rate limit events are logged at WARNING level for monitoring
- [x] Optional retry logic with exponential backoff is implemented
- [x] Retry logic can be enabled/disabled via environment variable
- [x] Documentation updated with rate limit information
- [x] Documentation includes retry configuration instructions
- [x] All 7 MCP tools handle rate limit errors consistently
- [x] Tests cover rate limit detection and error handling
- [x] Tests cover retry logic (if implemented)
- [x] Tests verify logging behavior for rate limits

## Files Modified

1. `src/todoist_mcp/server.py` - Add rate limit detection and handling
   - Add `is_rate_limit_error()` helper function
   - Add `retry_with_backoff()` helper function (optional)
   - Add retry configuration (optional)
   - Update error handling in all 7 tool functions

2. `tests/test_server.py` - Add comprehensive rate limit tests
   - Test `is_rate_limit_error()` detection logic
   - Test rate limit error handling for all tools
   - Test logging behavior for rate limits
   - Test retry logic (if implemented)

3. `docs/api.md` - Update documentation
   - Update rate limits section
   - Add rate limit handling explanation
   - Add retry configuration instructions
   - Add best practices for avoiding rate limits

4. `README.md` - Add rate limit handling to features
   - Mention rate limit handling in Features section

## Related Issues and Tasks

### Depends On

None - This is a standalone enhancement

### Blocks

None - Nice to have feature

### Related

- GitHub Issue #7: Logging infrastructure (completed) - Logging foundation enables rate limit event logging
- GitHub Issue #5: Input validation (completed) - Validation patterns inform error handling approach

### Enables

- Future: Rate limit monitoring dashboard
- Future: Advanced retry strategies (read Retry-After header)
- Future: Request throttling to prevent rate limits proactively
- Future: Rate limit usage tracking and alerting

## References

- [GitHub Issue #8](https://github.com/denhamparry/todoist-mcp/issues/8)
- [Todoist API Documentation](https://developer.todoist.com/rest/v2/)
- [Todoist API Rate Limits](https://developer.todoist.com/rest/v2/#rate-limits)
- [todoist-api-python Library](https://github.com/Doist/todoist-api-python)
- [Feature Request: Automatic backoff when rate limited](https://github.com/Doist/todoist-api-python/issues/38)
- [How to Avoid HTTP Error 429 (Too Many Requests) Python - API Tutorial](https://codelucky.com/how-to-avoid-http-error-429-python-api-tutorial/)
- [What is HTTP Error 429 Too Many Request and How to Fix it](https://scrapfly.io/blog/posts/what-is-http-error-429-too-many-requests)

## Notes

### Key Insights

1. **User Experience First**: Clear error messages provide immediate value even without retry logic
2. **Layered Implementation**: Can implement in phases (detection → messaging → retry → advanced features)
3. **Optional Retry**: Making retry optional gives users control and avoids unexpected delays
4. **Exponential Backoff**: Reduces server load and increases success rate vs. fixed delays
5. **Logging is Critical**: Rate limit events need monitoring for capacity planning

### Alternative Approaches Considered

1. **Always retry automatically** - Not chosen ❌
   - Pro: Reduces transient failures automatically
   - Con: Can cause unexpected delays in user experience
   - Con: Users have no control over behavior

2. **Read Retry-After header** - Deferred for future enhancement ⏭️
   - Pro: More accurate retry timing
   - Con: Requires access to response headers from exception
   - Con: todoist-api-python may not expose headers in exception
   - Note: Would require investigating library internals

3. **Implement request throttling** - Deferred for future enhancement ⏭️
   - Pro: Prevents rate limits proactively
   - Con: More complex implementation
   - Con: Requires tracking request counts and time windows
   - Note: Better as a separate feature after rate limit handling

4. **Chosen Approach: Detection + Clear Messaging + Optional Retry** ✅
   - Pro: Provides immediate value with clear error messages
   - Pro: Gives users control via configuration
   - Pro: Foundation for future enhancements
   - Pro: Relatively simple to implement and test
   - Pro: Consistent with existing error handling patterns

### Best Practices

1. **Error Message Design**: Include actionable guidance ("wait a few minutes and try again")
2. **Rate Limit Context**: Tell users the limit (450 requests per 15 minutes) so they understand
3. **Logging Strategy**: Use WARNING for rate limits (not ERROR) since it's expected behavior
4. **Testing**: Mock rate limit errors to avoid hitting actual API limits during tests
5. **Configuration**: Use environment variables for optional features (retry logic)
6. **Exponential Backoff**: Start small (2s) and double each retry to reduce server load

### Implementation Priority

**High Priority (MVP):**

- Step 1: Rate limit detection helper
- Step 2-3: Update error handling in all tools
- Step 6: Add basic tests

**Medium Priority (Nice to have):**

- Step 4: Optional retry logic
- Step 6: Comprehensive retry tests

**Low Priority (Future):**

- Step 5: Documentation updates
- Advanced features (read Retry-After header, request throttling)

### Security Considerations

- No API token logging (already handled by existing logging)
- Retry delays don't block other users (async/await pattern)
- Max retries prevents infinite loops
- Rate limit info doesn't expose sensitive details
