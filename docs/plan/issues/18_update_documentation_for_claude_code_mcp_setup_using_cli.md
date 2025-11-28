# GitHub Issue #18: Update documentation for Claude Code MCP setup using CLI

**Issue:** [#18](https://github.com/denhamparry/todoist-mcp/issues/18)
**Status:** Open
**Labels:** documentation
**Date:** 2025-11-28

## Problem Statement

The current documentation only shows how to manually configure the MCP server by editing JSON configuration files. However, Claude Code now supports a CLI command `claude mcp add` for easier setup, but the documentation doesn't mention it.

### Current Behavior

- README.md lines 70-102 only document manual JSON configuration method
- Users attempting to use `claude mcp add` command encounter errors
- No guidance on the correct CLI command syntax
- Missing verification steps after configuration
- No troubleshooting tips for CLI-based setup

**Example user error:**

```bash
claude mcp add --transport stdio todoist \
  --env TODOIST_API_TOKEN=<REDACTED> \
  --env LOG_LEVEL=INFO \
  -- /run/current-system/sw/bin/uv --directory /Users/lewis/git/denhamparry/todoist-mcp/main

# Result: ✗ Failed to connect
```

**Root cause:** Missing `run` command and script name `todoist-mcp` in the command.

### Expected Behavior

- Documentation shows **CLI method first** (recommended, easier)
- Correct command syntax for both `uv` and `python` methods
- Verification steps using `claude mcp list`
- Manual JSON configuration retained as alternative
- Clear explanation of differences between methods
- Troubleshooting tips for common CLI setup issues

## Current State Analysis

### Relevant Code/Config

**README.md** (lines 70-102) - "Usage with Claude Code" section:

Currently only documents manual JSON configuration:

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

Also shows `uv` variant but no CLI method.

### Related Context

**Claude Code CLI Documentation:**

- `claude mcp add` command is the modern, recommended approach
- Automatically handles JSON configuration
- Provides connection testing
- More user-friendly than manual JSON editing

**Project Structure:**

- Entry point: `python -m todoist_mcp.server`
- Package script: `todoist-mcp` (defined in pyproject.toml)
- Both `uv` and `python` methods work

**Dependencies:**

- None - purely documentation update
- No code changes required

## Solution Design

### Approach

Update the "Usage with Claude Code" section to:

1. **Lead with CLI method** - Most user-friendly approach
2. **Show both execution methods** - `uv` (recommended) and `python`
3. **Include verification** - How to confirm setup worked
4. **Retain JSON configuration** - As alternative/reference
5. **Add troubleshooting** - Common issues and fixes

**Rationale:**

- CLI method is easier for users (no manual JSON editing)
- Following modern best practices (CLI first, manual second)
- Prevents common errors like the one reported in issue
- Provides complete setup-to-verification workflow

### Implementation

**Section Structure:**

```markdown
## Usage with Claude Code

### Recommended: Using CLI (Easiest)

The `claude mcp add` command automatically configures the MCP server for you.

#### Using uv (Recommended)

[Command with full path explanation]

#### Using System Python

[Alternative command]

#### Verification

[How to check it worked]

### Alternative: Manual Configuration

For advanced users or troubleshooting, you can manually edit the configuration file.

[Existing JSON configuration examples]

### Troubleshooting

[Common issues and solutions]
```

**Specific Changes:**

1. **Add CLI section** with complete commands
2. **Explain parameters** (--transport, --env, --)
3. **Show verification** using `claude mcp list`
4. **Move JSON config** to "Alternative" subsection
5. **Add troubleshooting** tips for CLI errors

### Benefits

1. **Easier Setup** - Users can copy-paste a single command
2. **Prevents Errors** - Correct syntax documented clearly
3. **Better UX** - Follows modern CLI-first approach
4. **Complete Workflow** - Setup through verification in one place
5. **Backwards Compatible** - JSON method still available for advanced users

## Implementation Plan

### Step 1: Backup Current Documentation

**File:** `README.md`

**Action:**
Understand current content to ensure no information is lost during restructuring.

**Current lines 70-102:**

- Title: "Usage with Claude Code"
- Two JSON configuration examples (python and uv)
- Environment variable setup

**Testing:**

```bash
# Review current section
sed -n '70,102p' README.md
```

### Step 2: Add CLI Method Section

**File:** `README.md`

**Changes:**
Replace lines 70-102 with new structure starting with CLI method.

**New Content:**

```markdown
## Usage with Claude Code

### Recommended: Using CLI (Easiest)

The `claude mcp add` command automatically configures the MCP server for you. This is the easiest and recommended method.

#### Using uv (Recommended)

```bash
claude mcp add --transport stdio todoist \
  --env TODOIST_API_TOKEN=your_token_here \
  --env LOG_LEVEL=INFO \
  -- uv run --directory /path/to/todoist-mcp todoist-mcp
```

Replace `/path/to/todoist-mcp` with the actual path where you cloned this repository.

**Example:**

```bash
claude mcp add --transport stdio todoist \
  --env TODOIST_API_TOKEN=abc123xyz \
  --env LOG_LEVEL=INFO \
  -- uv run --directory /Users/lewis/git/todoist-mcp todoist-mcp
```

#### Using System Python

If you prefer not to use `uv`, you can use Python directly:

```bash
claude mcp add --transport stdio todoist \
  --env TODOIST_API_TOKEN=your_token_here \
  --env LOG_LEVEL=INFO \
  -- python -m todoist_mcp.server
```

**Note:** When using system Python, ensure you've activated the virtual environment first, or provide the full path to the Python interpreter in your project's virtual environment.

#### Verification

After running the command, verify the server is configured correctly:

```bash
claude mcp list
```

You should see `todoist` in the list of configured MCP servers with a status indicator showing it's ready.

### Alternative: Manual Configuration

For advanced users or if you need to troubleshoot, you can manually edit the Claude Code MCP configuration file.

**Location:**

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Add the following to your MCP settings:

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

Or if using `uv`:

```json
{
  "mcpServers": {
    "todoist": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/todoist-mcp", "todoist-mcp"],
      "env": {
        "TODOIST_API_TOKEN": "your_token_here",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Troubleshooting Setup

**Issue: "Failed to connect" error**

If you see `✗ Failed to connect` after running `claude mcp add`:

1. **Check the command syntax** - Ensure you included `run` and the script name:
   - ✓ Correct: `-- uv run --directory /path/to/todoist-mcp todoist-mcp`
   - ✗ Wrong: `-- uv --directory /path/to/todoist-mcp`

2. **Verify the path** - Make sure the directory path is absolute and correct:

   ```bash
   ls -la /path/to/todoist-mcp/pyproject.toml  # Should exist
   ```

3. **Test the server manually** - Run the server directly to check for errors:

   ```bash
   cd /path/to/todoist-mcp
   uv run todoist-mcp
   # Should start without errors (press Ctrl+C to stop)
   ```

4. **Check your API token** - Verify it's valid:

   ```bash
   # Test the token manually with curl
   # Use your actual API token from Todoist
   curl -H "Authorization: Bearer \$TODOIST_API_TOKEN" \
     https://api.todoist.com/rest/v2/projects
   # Should return your projects, not 401 error
   ```

**Issue: Server not appearing in `claude mcp list`**

1. **Restart Claude Code** - The configuration may need a restart to take effect
2. **Check the configuration file manually** - Verify the JSON was written correctly
3. **Look for syntax errors** - Ensure the JSON is valid (no trailing commas, proper quotes)

For more troubleshooting help, see [docs/troubleshooting.md](docs/troubleshooting.md).

````text
(End of new content)
````

**Testing:**

```bash
# Verify new section is in place
grep -A 5 "Recommended: Using CLI" README.md

# Check troubleshooting section added
grep -A 3 "Failed to connect" README.md
```

### Step 3: Update Logging Section Reference

**File:** `README.md`

**Changes:**
The logging section (lines 104-195) currently shows manual JSON configuration examples. Update the example to mention both methods:

**Current** (lines 116-131):

````markdown
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
```
````

**Update to:**

````markdown
Or when configuring the MCP server (manual configuration method):

```json
{
  "mcpServers": {
    "todoist": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/todoist-mcp", "todoist-mcp"],
      "env": {
        "TODOIST_API_TOKEN": "your_token_here",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

When using the CLI method (`claude mcp add`), the `LOG_LEVEL` environment variable is set with the `--env` flag:

```bash
claude mcp add --transport stdio todoist \
  --env TODOIST_API_TOKEN=your_token_here \
  --env LOG_LEVEL=DEBUG \
  -- uv run --directory /path/to/todoist-mcp todoist-mcp
```
````

**Testing:**

```bash
# Verify logging section updated
sed -n '104,145p' README.md | grep -A 3 "CLI method"
```

### Step 4: Add Cross-Reference to Support Section

**File:** `README.md`

**Changes:**
The Support section (around line 360) already links to troubleshooting. Ensure it's clear this covers setup issues too.

**Current** (lines 360-365):

````markdown
## Support

- **Troubleshooting**: [docs/troubleshooting.md](docs/troubleshooting.md)
- **Issues**: https://github.com/denhamparry/todoist-mcp/issues
- **Todoist API Docs**: https://developer.todoist.com/rest/v2/
- **MCP Specification**: https://modelcontextprotocol.io/
- **Claude Code**: https://docs.claude.com/en/docs/claude-code
````

**Update to:**

````markdown
## Support

- **Troubleshooting**: [docs/troubleshooting.md](docs/troubleshooting.md) - Setup, runtime, and MCP integration issues
- **Issues**: https://github.com/denhamparry/todoist-mcp/issues
- **Todoist API Docs**: https://developer.todoist.com/rest/v2/
- **MCP Specification**: https://modelcontextprotocol.io/
- **Claude Code**: https://docs.claude.com/en/docs/claude-code
- **Claude MCP CLI**: https://docs.anthropic.com/claude/docs/claude-code#mcp-servers
````

**Testing:**

```bash
# Verify support section has MCP CLI link
grep "Claude MCP CLI" README.md
```

### Step 5: Validate Documentation

**File:** `README.md`

**Changes:**
Run pre-commit hooks to ensure markdown formatting is correct.

**Testing:**

```bash
# Check markdown linting
pre-commit run --files README.md

# Verify links work (manually check in browser or with link checker)
grep -o 'https://[^)]*' README.md

# Check all code blocks are properly formatted
grep -c '```' README.md  # Should be even number
```

## Testing Strategy

### Manual Testing

**Test Case 1: CLI Method with uv**

1. Follow the CLI method instructions exactly as documented
2. Run the `claude mcp add` command with `uv`
3. Verify with `claude mcp list`
4. Test in Claude Code that todoist tools are available

**Expected:**

- Command succeeds without "Failed to connect" error
- Server appears in `claude mcp list`
- Tools work in Claude Code session

**Test Case 2: CLI Method with Python**

1. Follow the Python variant of CLI method
2. Ensure virtual environment is activated
3. Run the command and verify

**Expected:**

- Command succeeds
- Server configured correctly

**Test Case 3: Manual Configuration Method**

1. Follow the manual configuration steps
2. Edit the JSON file directly
3. Restart Claude Code
4. Verify server works

**Expected:**

- JSON configuration is valid
- Server appears after restart
- Tools work correctly

**Test Case 4: Troubleshooting Steps**

1. Intentionally create the error from the issue (missing `run` command)
2. Follow the troubleshooting steps
3. Verify they lead to the correct solution

**Expected:**

- Error reproduced
- Troubleshooting steps identify the problem
- Solution fixes the error

**Test Case 5: Verification Steps**

1. Set up server using CLI method
2. Run `claude mcp list` as documented
3. Confirm output matches description

**Expected:**

- Verification command works
- Output clearly shows server status

### Documentation Quality Checks

1. **Accuracy** - All commands have been tested and work
2. **Completeness** - Both CLI and manual methods documented
3. **Clarity** - Step-by-step instructions are easy to follow
4. **Examples** - Real path examples provided (with placeholder notation)
5. **Troubleshooting** - Common errors from issue #18 are addressed
6. **Links** - All internal and external links are valid
7. **Formatting** - Markdown renders correctly
8. **Consistency** - Terminology and style consistent throughout

### Verification Commands

```bash
# Check README structure
grep "^##" README.md | grep -A 2 "Usage with Claude Code"

# Verify CLI method is documented first
sed -n '/## Usage with Claude Code/,/## Logging/p' README.md | grep -n "Recommended: Using CLI"

# Check troubleshooting section exists
grep -A 5 "Troubleshooting Setup" README.md

# Verify both uv and python methods documented
grep -c "uv run --directory" README.md  # Should be >= 2
grep -c "python -m todoist_mcp.server" README.md  # Should be >= 2

# Check verification section exists
grep -A 3 "claude mcp list" README.md

# Validate markdown formatting
pre-commit run markdownlint --files README.md
```

## Success Criteria

- [ ] README.md "Usage with Claude Code" section updated with CLI-first approach
- [ ] CLI method using `uv` documented with correct syntax
- [ ] CLI method using `python` documented as alternative
- [ ] Verification steps using `claude mcp list` included
- [ ] Manual JSON configuration retained as "Alternative" method
- [ ] Troubleshooting section covers "Failed to connect" error
- [ ] Troubleshooting section covers missing `run` command issue
- [ ] Example commands use placeholder paths (e.g., `/path/to/todoist-mcp`)
- [ ] API token shown as `your_token_here` (no real tokens)
- [ ] Logging section updated to mention both CLI and manual methods
- [ ] Support section includes link to Claude MCP CLI documentation
- [ ] All markdown formatting is valid (pre-commit passes)
- [ ] Documentation tested manually and commands work

## Files Modified

1. `README.md` - Lines 70-102 (Usage with Claude Code section) - Major restructuring
2. `README.md` - Lines 116-131 (Logging section example) - Minor update to mention CLI method
3. `README.md` - Lines 360-365 (Support section) - Add Claude MCP CLI documentation link

## Related Issues and Tasks

### Depends On

- None (standalone documentation task)

### Blocks

- None (improves user experience but doesn't block other work)

### Related

- Issue #10 - Troubleshooting guide (setup troubleshooting can reference this)
- General onboarding improvements

### Enables

- Easier setup for new users
- Fewer "Failed to connect" support issues
- Modern CLI-first approach adoption
- Better user experience overall

## References

- [GitHub Issue #18](https://github.com/denhamparry/todoist-mcp/issues/18)
- [Claude Code Documentation](https://docs.anthropic.com/claude/docs/claude-code)
- [Claude MCP CLI Documentation](https://docs.anthropic.com/claude/docs/claude-code#mcp-servers)
- [MCP Specification](https://modelcontextprotocol.io/)
- Current README.md documentation (lines 70-102)

## Notes

### Key Insights

1. **User Error Provides Clarity** - The reported error shows exactly what's missing in docs
2. **CLI-First is Modern** - Following current best practices by leading with CLI
3. **Backwards Compatibility** - Keeping JSON method ensures advanced users aren't blocked
4. **Complete Workflow** - Setup → Verification → Troubleshooting in one section
5. **Path Handling** - Absolute paths are critical for `--directory` flag

### Design Decisions

1. **CLI First** - Lead with easiest method, not just add it as alternative
2. **Both Execution Methods** - Document both `uv` (recommended) and `python` for flexibility
3. **Inline Troubleshooting** - Put troubleshooting in usage section, not just separate doc
4. **Real Examples** - Show actual command structure with placeholder notation
5. **Verification Required** - Don't just show setup, show how to confirm it worked

### Alternative Approaches Considered

1. **Add CLI as footnote to JSON config** - Why not chosen ❌
   - Doesn't emphasize that CLI is the recommended approach
   - Harder for users to find
   - Perpetuates manual JSON editing as primary method

2. **Only document CLI method** - Why not chosen ❌
   - Some users need manual config for advanced setups
   - Troubleshooting may require understanding the JSON structure
   - Removes flexibility

3. **Separate CLI and JSON into different sections** - Why not chosen ❌
   - Creates confusion about which to use
   - "Recommended" vs "Alternative" structure is clearer

4. **Chosen Approach: CLI First, JSON as Alternative** - Why selected ✅
   - Clear guidance on recommended method
   - Maintains flexibility for advanced users
   - Matches modern CLI-first documentation patterns
   - Addresses the exact issue reported (#18)

### Best Practices

1. **Test All Commands** - Every command in docs should be tested before publishing
2. **Use Placeholders** - Never include real tokens or specific user paths
3. **Show Verification** - Always include "how to confirm it worked" steps
4. **Troubleshoot Common Errors** - Document errors users will actually encounter
5. **Link to More Help** - Cross-reference troubleshooting guide for deeper issues
6. **Keep Examples Realistic** - Use plausible paths and realistic scenarios

### Common Mistakes to Avoid

1. **Don't forget `run` in uv command** - Main issue from #18
2. **Don't forget script name `todoist-mcp`** - Required for entry point
3. **Don't use relative paths** - `--directory` needs absolute path
4. **Don't assume virtual env** - Clarify when it's needed (Python method)
5. **Don't skip verification** - Users need to know if setup worked

### Monitoring and Maintenance

After implementation:

1. **Monitor GitHub Issues** - Track if "Failed to connect" errors decrease
2. **Gather User Feedback** - Ask if CLI method is easier
3. **Update as CLI Evolves** - Keep up with `claude mcp` command changes
4. **Test Periodically** - Verify commands still work with Claude Code updates
5. **Cross-Reference Troubleshooting** - Ensure troubleshooting.md stays in sync
