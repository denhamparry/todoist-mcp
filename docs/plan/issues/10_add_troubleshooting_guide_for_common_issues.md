# GitHub Issue #10: Add troubleshooting guide for common issues

**Issue:** [#10](https://github.com/denhamparry/todoist-mcp/issues/10)
**Status:** Open
**Labels:** documentation
**Date:** 2025-11-28

## Problem Statement

Users need a centralized troubleshooting guide to help them diagnose and fix common issues with the Todoist MCP server. Currently, troubleshooting information is scattered across different documentation files or not documented at all.

### Current Behavior

- No dedicated troubleshooting guide exists
- Setup issues and runtime errors lack centralized documentation
- Users must search through README, API docs, and integration testing docs to find solutions
- Common problems and solutions are not easily discoverable

### Expected Behavior

- Comprehensive troubleshooting guide at `docs/troubleshooting.md`
- Covers setup issues, runtime errors, and MCP integration problems
- Includes debugging techniques and FAQ section
- Linked from README.md for easy discovery

## Current State Analysis

### Existing Documentation

**README.md** (lines 104-195):

- Contains logging configuration and debugging section
- Some basic troubleshooting for log levels
- Security notes about API tokens

**docs/api.md** (lines 264-333):

- Error handling section with common error scenarios
- Rate limit handling information (lines 292-333)
- Best practices for API usage

**docs/integration-testing.md** (lines 168-235):

- Comprehensive troubleshooting section for integration tests
- Covers: missing token, 401/403/404/429 errors, import errors
- Good examples that can be adapted for general troubleshooting

**src/todoist_mcp/server.py**:

- Logging infrastructure (lines 19-40)
- Validation error messages (lines 46-129)
- Rate limit detection (lines 132-152)
- Error handling in all tools with user-friendly messages

### Related Context

The project already has:

1. Comprehensive logging system with configurable levels
2. Input validation with clear error messages
3. Rate limit handling with helpful guidance
4. Integration testing guide with troubleshooting section
5. API documentation with error scenarios

Missing:

1. Centralized troubleshooting guide combining all common issues
2. Setup-specific troubleshooting (installation, environment)
3. MCP integration troubleshooting (Claude Desktop configuration)
4. Debugging techniques using MCP Inspector
5. FAQ section for quick reference

## Solution Design

### Approach

Create a comprehensive `docs/troubleshooting.md` that consolidates and expands on existing troubleshooting content, organized by issue category:

1. **Setup Issues** - Installation, environment configuration, API token setup
2. **Runtime Issues** - Task operations, validation errors, API failures
3. **MCP Integration Issues** - Claude Desktop configuration, server connectivity
4. **Debugging Techniques** - Log analysis, MCP Inspector, testing
5. **FAQ** - Quick answers to common questions

### Implementation

**File Structure:**

```markdown
# Troubleshooting Guide

## Table of Contents
- Quick Troubleshooting Checklist
- Setup Issues
- Runtime Issues
- MCP Integration Issues
- Debugging Techniques
- FAQ
- Getting Help

Each section:
- Problem symptom
- Cause explanation
- Step-by-step solution
- Verification steps
```

**Content Sources:**

- Adapt integration-testing.md troubleshooting (authentication, rate limits)
- Extract logging/debugging info from README.md
- Document MCP configuration issues (based on README.md lines 70-102)
- Add validation error scenarios from server.py
- Create FAQ based on issue descriptions

### Benefits

1. **Improved User Experience** - One-stop resource for problem solving
2. **Reduced Support Burden** - Common issues documented with solutions
3. **Better Onboarding** - New users can self-diagnose setup problems
4. **Comprehensive Coverage** - Spans setup, runtime, and integration
5. **Easy Discovery** - Linked prominently from README

## Implementation Plan

### Step 1: Create Troubleshooting Guide Structure

**File:** `docs/troubleshooting.md`

**Changes:**

- Create new file with table of contents
- Add introduction explaining when to use this guide
- Include quick troubleshooting checklist for fast diagnosis
- Set up main sections: Setup, Runtime, MCP Integration, Debugging, FAQ

**Testing:**

```bash
# Verify file is created and has proper structure
cat docs/troubleshooting.md | head -30
```

### Step 2: Document Setup Issues

**File:** `docs/troubleshooting.md`

**Changes:**
Add setup issues section covering:

1. **API token not found**
   - Symptom: `TODOIST_API_TOKEN environment variable not set`
   - Cause: Missing or incorrectly configured `.env` file
   - Solution: Create `.env` from template, verify token from Todoist
   - Verification: `grep TODOIST_API_TOKEN .env`

2. **Import/Module errors**
   - Symptom: `ModuleNotFoundError: No module named 'mcp'`
   - Cause: Dependencies not installed
   - Solution: Run `uv sync` or `pip install -e ".[dev]"`
   - Verification: `pytest --version`

3. **Invalid API token**
   - Symptom: 401 Unauthorized errors
   - Cause: Incorrect token, expired, or typos
   - Solution: Regenerate token in Todoist, update `.env`
   - Reference: Link to Todoist API token help page

**Testing:**

```bash
# Verify setup section is comprehensive
grep -A 5 "API token not found" docs/troubleshooting.md
```

### Step 3: Document Runtime Issues

**File:** `docs/troubleshooting.md`

**Changes:**
Add runtime issues section covering:

1. **Invalid task ID errors**
   - Symptom: `Task ID does not exist`
   - Cause: Incorrect task ID or task already deleted
   - Solution: Use `todoist_get_tasks` to find correct IDs
   - Example: Show how to get task list first

2. **Rate limit errors (429)**
   - Symptom: `Todoist API rate limit exceeded`
   - Cause: Too many requests in 15-minute window
   - Solution: Wait 15 minutes, reduce request frequency
   - Details: Standard plans ~450 requests per 15 minutes

3. **Validation errors**
   - Priority validation: Must be 1-4
   - Task ID validation: Cannot be empty
   - Labels validation: Must be list of strings
   - Examples from server.py validation functions

4. **Project/Label not found**
   - Symptom: 404 errors
   - Cause: Invalid project or label IDs
   - Solution: Use `todoist_get_projects` and `todoist_get_labels`

**Testing:**

```bash
# Verify runtime section covers key scenarios
grep -A 3 "Rate limit" docs/troubleshooting.md
```

### Step 4: Document MCP Integration Issues

**File:** `docs/troubleshooting.md`

**Changes:**
Add MCP integration issues section covering:

1. **Server not appearing in Claude Desktop**
   - Symptom: Server not listed in available MCP servers
   - Cause: Incorrect configuration file location or JSON syntax
   - Solution:
     - Check config file path for Claude Desktop
     - Validate JSON syntax
     - Restart Claude Desktop
   - Example: Show correct configuration from README

2. **Server crashes on startup**
   - Symptom: Server immediately exits when launched
   - Cause: Missing environment variables, Python version, import errors
   - Solution:
     - Check `TODOIST_API_TOKEN` is set in config
     - Verify Python 3.10+ is installed
     - Check logs for specific error
   - Debug: Run `uv run python -m todoist_mcp.server` manually

3. **Server connection errors**
   - Symptom: Claude Desktop can't connect to server
   - Cause: Server process not running or communication issues
   - Solution: Check stderr logs, verify command path

4. **Environment variables not loading**
   - Symptom: Token errors despite config having token
   - Cause: Environment variables in MCP config not applied
   - Solution: Show correct env format in mcpServers config

**Testing:**

```bash
# Verify MCP section has configuration examples
grep -A 10 "Server not appearing" docs/troubleshooting.md
```

### Step 5: Document Debugging Techniques

**File:** `docs/troubleshooting.md`

**Changes:**
Add debugging techniques section covering:

1. **Using log levels**
   - Set `LOG_LEVEL=DEBUG` in `.env` or MCP config
   - Explain log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
   - Show example debug output
   - Location: Logs go to stderr

2. **Testing with MCP Inspector**
   - Command: `npx @modelcontextprotocol/inspector python -m todoist_mcp.server`
   - Benefits: Interactive testing of tools
   - How to use: Test individual tool calls

3. **Manual server testing**
   - Run server directly: `uv run python -m todoist_mcp.server`
   - Check startup logs
   - Verify environment variables loaded

4. **Running unit tests**
   - Quick validation: `pytest tests/test_server.py`
   - Coverage check: `pytest --cov=src/todoist_mcp`
   - Integration tests: See integration-testing.md

5. **Verifying API token manually**
   - Use curl to test token validity
   - Command example: `curl -H "Authorization: Bearer $TODOIST_API_TOKEN" https://api.todoist.com/rest/v2/projects`

**Testing:**

```bash
# Verify debugging section is actionable
grep -A 5 "log levels" docs/troubleshooting.md
```

### Step 6: Create FAQ Section

**File:** `docs/troubleshooting.md`

**Changes:**
Add FAQ section with common questions:

1. **Q: How do I know if my API token is working?**
   - A: Run server with DEBUG logging and check startup logs, or use curl to test

2. **Q: Can I use this with my personal Todoist account?**
   - A: Yes, but use a dedicated test account for integration tests

3. **Q: Why aren't my tasks showing up?**
   - A: Check project_id filter, verify tasks exist in Todoist web app, check rate limits

4. **Q: How do I find task IDs?**
   - A: Use `todoist_get_tasks` tool first to list all tasks with IDs

5. **Q: What's the difference between unit and integration tests?**
   - A: Unit tests use mocks (no API calls), integration tests use real API (see integration-testing.md)

6. **Q: Is my API token safe?**
   - A: Never commit .env file, it's gitignored. Logs never show tokens. Use environment variables.

7. **Q: Where can I find more help?**
   - A: Check API docs, integration testing guide, open GitHub issue

**Testing:**

```bash
# Verify FAQ covers key questions
grep "^Q:" docs/troubleshooting.md | wc -l  # Should be at least 7
```

### Step 7: Link from README

**File:** `README.md`

**Changes:**
Add troubleshooting link to Support section (around line 359):

```markdown
## Support

- **Troubleshooting**: [docs/troubleshooting.md](docs/troubleshooting.md)
- **Issues**: https://github.com/denhamparry/todoist-mcp/issues
- **Todoist API Docs**: https://developer.todoist.com/rest/v2/
- **MCP Specification**: https://modelcontextprotocol.io/
- **Claude Code**: https://docs.claude.com/en/docs/claude-code
```

**Testing:**

```bash
# Verify link is added and works
grep -A 5 "## Support" README.md
```

### Step 8: Add Cross-References

**File:** `docs/troubleshooting.md`

**Changes:**

Add "See Also" section at end with links to:

- `docs/api.md` - For API documentation and error details
- `docs/integration-testing.md` - For integration test setup
- `README.md` - For installation and usage
- Todoist API documentation
- MCP Inspector documentation

**Testing:**

```bash
# Verify cross-references exist
grep -A 5 "See Also" docs/troubleshooting.md
```

## Testing Strategy

### Manual Testing

**Test Case 1: Navigation and Discoverability**

1. Open README.md
2. Find Support section
3. Click troubleshooting link
4. Verify it opens troubleshooting guide

**Expected:** Easy to find from README

**Test Case 2: Setup Issue Resolution**

1. Simulate missing API token scenario
2. Follow troubleshooting steps for "API token not found"
3. Verify solution resolves the issue

**Expected:** Clear steps that work

**Test Case 3: Runtime Issue Resolution**

1. Simulate rate limit error
2. Follow troubleshooting steps for "Rate limit errors"
3. Verify explanation and solution are clear

**Expected:** Actionable guidance

**Test Case 4: MCP Integration Resolution**

1. Review MCP configuration troubleshooting
2. Verify examples match README configuration
3. Check solution steps are complete

**Expected:** Configuration examples are accurate

**Test Case 5: Debugging Technique Usage**

1. Follow debug logging instructions
2. Enable DEBUG level
3. Verify log output matches description

**Expected:** Debugging steps work as documented

### Documentation Quality Checks

1. **Completeness** - All issues from issue #10 are documented
2. **Accuracy** - Information matches actual behavior and code
3. **Clarity** - Solutions are step-by-step and actionable
4. **Examples** - Include code snippets and command examples
5. **Cross-references** - Links to related docs are accurate
6. **Formatting** - Markdown renders correctly
7. **TOC** - Table of contents links work

### Verification Commands

```bash
# Check file exists
ls -la docs/troubleshooting.md

# Verify structure
grep "^#" docs/troubleshooting.md

# Check link from README
grep "troubleshooting.md" README.md

# Validate markdown
# (Use pre-commit or markdownlint if available)
pre-commit run --files docs/troubleshooting.md

# Check all issues from #10 are covered
grep -i "API token not found" docs/troubleshooting.md
grep -i "ModuleNotFoundError" docs/troubleshooting.md
grep -i "Task ID does not exist" docs/troubleshooting.md
grep -i "rate limit" docs/troubleshooting.md
grep -i "Server not appearing" docs/troubleshooting.md
```

## Success Criteria

- [x] `docs/troubleshooting.md` created with comprehensive content
- [x] Setup issues section covers: API token, import errors, authentication
- [x] Runtime issues section covers: task IDs, rate limits, validation, 404 errors
- [x] MCP integration section covers: server not appearing, crashes, connection errors
- [x] Debugging techniques section covers: logging, MCP Inspector, manual testing
- [x] FAQ section with at least 7 common questions
- [x] README.md links to troubleshooting guide in Support section
- [x] Cross-references to related documentation
- [x] All markdown properly formatted and renders correctly
- [x] Issues from GitHub issue #10 are all documented

## Files Modified

1. `docs/troubleshooting.md` (new) - Comprehensive troubleshooting guide
2. `README.md` - Add link to troubleshooting guide in Support section

## Related Issues and Tasks

### Depends On

- None (standalone documentation task)

### Blocks

- None (nice-to-have documentation improvement)

### Related

- Issue #7 - Logging infrastructure (provides DEBUG logging for troubleshooting)
- Issue #8 - Rate limit handling (rate limit troubleshooting section)
- Issue #9 - Integration testing docs (integration test troubleshooting)

### Enables

- Better user self-service for common problems
- Reduced support burden on maintainers
- Improved onboarding experience for new users

## References

- [GitHub Issue #10](https://github.com/denhamparry/todoist-mcp/issues/10)
- [Todoist API Documentation](https://developer.todoist.com/rest/v2/)
- [Todoist API Token Guide](https://todoist.com/help/articles/find-your-api-token-Jpzx9IIlB)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
- Existing docs:
  - `README.md` - Installation, logging, examples
  - `docs/api.md` - Error handling, rate limits
  - `docs/integration-testing.md` - Integration test troubleshooting

## Notes

### Key Insights

1. **Content Already Exists** - Much troubleshooting content scattered across existing docs
2. **Consolidation Value** - Main value is bringing it all together in one place
3. **Issue #10 is Comprehensive** - GitHub issue provides excellent outline of issues to cover
4. **Integration Testing Guide** - Has great troubleshooting examples to adapt
5. **User Perspective** - Organize by symptom/problem, not by code structure

### Design Decisions

1. **Organize by Issue Category** - Setup, Runtime, MCP Integration for easy navigation
2. **Symptom → Solution Format** - Start with what user sees, then explain cause and fix
3. **Include Examples** - Code snippets, commands, and expected output
4. **Cross-Reference, Don't Duplicate** - Link to detailed guides (integration-testing.md) rather than duplicate
5. **Quick Reference** - Table of contents and FAQ for fast answers

### Best Practices

1. **Keep It Updated** - Update troubleshooting guide when new issues are discovered
2. **User Feedback** - Gather feedback on which issues are most common
3. **Link from Errors** - Consider referencing troubleshooting guide in error messages
4. **Examples Matter** - Real commands and output help users verify they're on right track
5. **Validation** - Test all solutions actually work before documenting
