# Todoist MCP Server - API Documentation

Complete reference for all MCP tools provided by the Todoist MCP server.

## Tool Reference

### todoist_get_tasks

Retrieve tasks from Todoist with optional filtering.

**Parameters:**

- `project_id` (string, optional): Filter tasks by project ID
- `filter` (string, optional): Todoist filter query (e.g., "today", "p1", "overdue")

**Returns:** Formatted string containing list of tasks

**Example Response:**

```text
Found 3 task(s):

- [7890123456] Review pull request
  Due: tomorrow at 2pm
  Priority: P1 (Urgent)
  Labels: work, code-review

- [7890123457] Buy groceries
  Due: today
  Labels: personal

- [7890123458] Write documentation
  Priority: P2 (High)
```

**Usage Examples:**

```text
# Get all tasks
"Show me all my tasks"

# Get today's tasks
"What tasks do I have today?"

# Get high priority tasks
"Show me my urgent tasks"

# Get tasks in specific project
"List tasks in project 2234567890"
```

---

### todoist_create_task

Create a new task in Todoist.

**Parameters:**

- `content` (string, required): Task title
- `description` (string, optional): Detailed task description
- `project_id` (string, optional): Project ID to add task to
- `due_string` (string, optional): Natural language due date (e.g., "tomorrow", "next Monday at 3pm")
- `priority` (integer, optional): Task priority
  - `1` = Normal (default)
  - `2` = Medium
  - `3` = High
  - `4` = Urgent
- `labels` (array of strings, optional): List of label names to apply

**Returns:** Success message with task ID

**Example Response:**

```text
✓ Task created: Review pull request (ID: 7890123456)
```

**Usage Examples:**

```text
# Simple task
"Create a task to call the dentist"

# Task with due date
"Create a task 'Finish report' due tomorrow"

# Task with priority and labels
"Create an urgent task 'Fix production bug' with label 'work'"

# Complete task creation
"Create a task 'Team meeting' due next Monday at 2pm with high priority and labels 'work', 'meetings'"
```

---

### todoist_update_task

Update an existing task in Todoist.

**Parameters:**

- `task_id` (string, required): ID of the task to update
- `content` (string, optional): New task title
- `description` (string, optional): New task description
- `due_string` (string, optional): New due date
- `priority` (integer, optional): New priority (1-4)
- `labels` (array of strings, optional): New list of label names

**Returns:** Success message

**Example Response:**

```text
✓ Task 7890123456 updated successfully
```

**Usage Examples:**

```text
# Update title
"Update task 7890123456 to 'Review PR #123'"

# Change due date
"Change task 7890123456 due date to next week"

# Update priority
"Make task 7890123456 urgent priority"

# Update multiple fields
"Update task 7890123456: change title to 'Complete quarterly review', set due date to Friday, and make it high priority"
```

---

### todoist_complete_task

Mark a task as complete in Todoist.

**Parameters:**

- `task_id` (string, required): ID of the task to complete

**Returns:** Success message

**Example Response:**

```text
✓ Task 7890123456 marked as complete
```

**Usage Examples:**

```text
# Complete a task
"Complete task 7890123456"

# Mark as done
"Mark task 7890123456 as done"

# Finish task
"I finished task 7890123456"
```

---

### todoist_delete_task

Delete a task from Todoist permanently.

**Parameters:**

- `task_id` (string, required): ID of the task to delete

**Returns:** Success message

**Example Response:**

```text
✓ Task 7890123456 deleted
```

**Usage Examples:**

```text
# Delete a task
"Delete task 7890123456"

# Remove task
"Remove task 7890123456"
```

---

### todoist_get_projects

Get all projects from Todoist.

**Parameters:** None

**Returns:** Formatted string containing list of projects

**Example Response:**

```text
Found 4 project(s):

- [2234567890] Work
  ⭐ Favorite
- [2234567891] Personal
- [2234567892] Shopping
- [2234567893] Learning
  ⭐ Favorite
```

**Usage Examples:**

```text
# List all projects
"What projects do I have?"

# Show projects
"List my Todoist projects"

# Get project IDs
"Show me all project IDs"
```

---

### todoist_get_labels

Get all labels from Todoist.

**Parameters:** None

**Returns:** Formatted string containing list of labels

**Example Response:**

```text
Found 5 label(s):

- [2123456789] work
- [2123456790] personal
- [2123456791] urgent
- [2123456792] shopping
- [2123456793] reading
```

**Usage Examples:**

```text
# List all labels
"What labels do I have?"

# Show labels
"List my Todoist labels"

# Get label IDs
"Show me all label IDs"
```

## Filter Query Syntax

When using `todoist_get_tasks` with the `filter` parameter, you can use Todoist's powerful filter syntax:

### Common Filters

- `today` - Tasks due today
- `tomorrow` - Tasks due tomorrow
- `overdue` - Overdue tasks
- `no date` - Tasks without a due date
- `p1` - Priority 1 (urgent) tasks
- `p2` - Priority 2 (high) tasks
- `p3` - Priority 3 (medium) tasks
- `@label` - Tasks with specific label
- `#project` - Tasks in specific project

### Examples

```text
# Today's tasks
filter: "today"

# Urgent tasks due today
filter: "today & p1"

# Work tasks without a due date
filter: "@work & no date"

# All high priority tasks
filter: "p2 | p1"
```

## Error Handling

All tools return error messages in a user-friendly format when operations fail:

```text
Error fetching tasks: Invalid API token
Error creating task: Project ID not found
Error completing task: Task ID does not exist
```

Common error scenarios:

- Invalid or missing API token
- Invalid task/project/label IDs
- Network connectivity issues
- Rate limiting (429 errors)
- Invalid date formats

## Best Practices

1. **Get Task IDs First**: Use `todoist_get_tasks` to find task IDs before updating, completing, or deleting
2. **Natural Language Dates**: Use natural language for due dates (e.g., "tomorrow at 2pm")
3. **Project Organization**: Get project IDs with `todoist_get_projects` to organize tasks
4. **Labels for Categorization**: Use labels to categorize and filter tasks efficiently
5. **Priority Management**: Use priorities (1-4) to organize tasks by urgency
6. **Error Recovery**: If a tool returns an error, check IDs and try again

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

## Security Notes

- API token is stored in environment variables
- Never share or commit your API token
- The server does not log or expose API tokens
- All communication is over stdio (no network exposure)
