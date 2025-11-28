# GitHub Issue #9: Add integration test documentation

**Issue:** [#9](https://github.com/denhamparry/todoist-mcp/issues/9)
**Status:** Open
**Labels:** documentation
**Date:** 2025-11-28

## Problem Statement

The project has integration tests in `tests/test_integration.py` that test against the real Todoist API, but there is no documentation explaining how to set up, run, or safely use these tests. Developers need comprehensive documentation to:

- Understand integration testing prerequisites
- Set up the required environment variables
- Run integration tests safely without affecting production data
- Troubleshoot common issues
- Follow best practices for cleanup

### Current Behavior

- Integration tests exist but are undocumented
- No guidance on how to obtain or configure test credentials
- No safety guidelines about using dedicated test accounts
- No troubleshooting section for common API-related issues
- `.env.example` doesn't include integration test variables
- README.md has no integration testing section

### Expected Behavior

- Complete integration test documentation in `docs/integration-testing.md`
- README.md links to integration test documentation
- `.env.example` includes integration test variables with comments
- Clear step-by-step setup instructions
- Safety guidelines to prevent accidental data modification
- Troubleshooting section for common issues
- Example test output for reference

## Current State Analysis

### Existing Integration Tests

**File:** `tests/test_integration.py`

The integration tests cover:

- Getting tasks, projects, and labels
- Creating and deleting tasks
- Updating task properties
- Completing tasks
- Working with due dates
- Project-specific task creation
- Filtering tasks by project

**Test markers:**

- `@pytest.mark.integration` - All integration tests use this marker
- `@pytest.mark.asyncio` - Tests are asynchronous

**Fixtures used:**

- `todoist_client` - Creates real Todoist API client from `TODOIST_API_TOKEN`
- `test_project_id` - Gets test project ID from `TODOIST_TEST_PROJECT_ID`

### Environment Variables Required

From `tests/conftest.py:17-31`:

1. **`TODOIST_API_TOKEN`** (required) - Real Todoist API token
   - Tests skip if not set
   - Used to create TodoistAPIAsync client

2. **`TODOIST_TEST_PROJECT_ID`** (optional) - Specific test project ID
   - Tests requiring project skip if not set
   - Used for project-specific test isolation

### Current Documentation

**README.md** includes:

- Development section with unit test commands
- No mention of integration tests
- No section on environment setup for integration tests

**`.env.example`** includes:

- `TODOIST_API_TOKEN` (for server operation)
- `LOG_LEVEL` (for logging)
- Missing integration test variables

**Docs directory:**

- `docs/api.md` - Tool API documentation
- `docs/setup.md` - Development setup guide
- `docs/plan.md` - Development plan
- No integration testing documentation

## Solution Design

### Approach

Create comprehensive integration test documentation that:

1. **Educates developers** on integration vs unit testing differences
2. **Provides clear setup steps** with safety-first approach
3. **Documents all required environment variables** with examples
4. **Includes troubleshooting** for common API-related issues
5. **Shows example output** so developers know what to expect
6. **Links from README** for discoverability

### Implementation

Create new file: `docs/integration-testing.md`

**Structure:**

1. Overview - What integration tests are and why they exist
2. Prerequisites - Account setup, API token retrieval
3. Environment Setup - Variables, .env configuration
4. Safety Guidelines - Test accounts, test projects, cleanup
5. Running Tests - Commands, filtering, coverage
6. Test Coverage - What's tested
7. Troubleshooting - Common issues and solutions
8. Example Output - What successful runs look like
9. Best Practices - Do's and don'ts

**Update `.env.example`:**

- Add `TODOIST_TEST_PROJECT_ID` with comment
- Explain integration testing context

**Update README.md:**

- Add Integration Testing section
- Link to new documentation
- Clarify difference from unit tests

### Benefits

- **Safety** - Developers understand how to avoid production data issues
- **Clarity** - Step-by-step setup reduces friction
- **Troubleshooting** - Common issues documented with solutions
- **Onboarding** - New contributors can quickly set up integration tests
- **Best practices** - Establishes testing standards for the project

## Implementation Plan

### Step 1: Create Integration Testing Documentation

**File:** `docs/integration-testing.md`

**Content structure:**

```markdown
# Integration Testing Guide

## Overview
[What integration tests are, why they exist, when to run them]

## Prerequisites
1. Todoist account (free or paid)
2. Dedicated test account recommended
3. API token access

## Getting Your API Token
[Step-by-step with screenshots or links]
- Visit Todoist settings
- Navigate to Integrations > Developer
- Copy API token
- Security best practices

## Creating a Test Project
[How to create a dedicated test project]

- Why use a dedicated project
- How to create it
- How to get the project ID

## Environment Setup
[Complete .env configuration]
```bash
# Required for integration tests
TODOIST_API_TOKEN=your_real_token_here

# Optional: Isolate tests to specific project
TODOIST_TEST_PROJECT_ID=1234567890
```

## Safety Guidelines

[Critical safety information]

- ⚠️ Use dedicated test account
- ⚠️ Use specific test project
- ⚠️ Tests create and delete real data
- ⚠️ Don't run against production projects
- ✅ Tests clean up after themselves

## Running Integration Tests

```bash
# Run all integration tests
pytest tests/test_integration.py -m integration -v

# Run specific test
pytest tests/test_integration.py::test_create_and_delete_task_workflow -v

# Run with coverage
pytest tests/test_integration.py -m integration --cov=src/todoist_mcp
```

## What's Tested

[List of test coverage areas]

- Task CRUD operations
- Project management
- Label operations
- Due date handling
- Task filtering

## Troubleshooting

[Common issues and solutions]

### Error: "TODOIST_API_TOKEN not set"

Solution: Set environment variable in .env

### Error: "401 Unauthorized"

Solution: Check token validity, regenerate if needed

### Error: "404 Not Found"

Solution: Verify project ID exists, check permissions

### Error: "Rate limit exceeded"

Solution: Wait and retry, reduce test frequency

## Example Output

[Show successful test run output]

## CI/CD Considerations

[Why integration tests aren't in CI]

- Require real credentials
- Create actual API load
- Run manually before releases

## Best Practices

- Run before major releases
- Keep test data minimal
- Clean up failed test data manually
- Monitor API quota usage
- Use test project isolation

```markdown

**Testing:**
```bash
# Verify markdown formatting
markdownlint docs/integration-testing.md

# Test that links work
# Manual verification
```

### Step 2: Update .env.example

**File:** `.env.example`

**Changes:**

```bash
# Todoist API Token
# Get your token: https://todoist.com/help/articles/find-your-api-token-Jpzx9IIlB
TODOIST_API_TOKEN=your_api_token_here

# Logging Configuration
# Supported levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
# Default: INFO
LOG_LEVEL=INFO

# Integration Testing (Optional)
# These variables are only needed if you want to run integration tests
# against the real Todoist API. See docs/integration-testing.md for details.
#
# IMPORTANT: Use a dedicated test account and test project to avoid
# affecting your production Todoist data.
#
# TODOIST_TEST_PROJECT_ID=1234567890  # Optional: Isolate tests to specific project
```

**Testing:**

```bash
# Verify format
cat .env.example

# Ensure no actual credentials
grep -v "your_" .env.example
```

### Step 3: Update README.md

**File:** `README.md`

**Changes:**

Add new section after "Development" section (~line 239):

```markdown
## Development

### Running Tests

**Unit Tests** (default - no API token required):

```bash
# Using uv
uv run pytest

# Using pip (with activated venv)
pytest

# With coverage report
pytest --cov=src/todoist_mcp --cov-report=html
```

**Integration Tests** (requires real Todoist API token):

Integration tests make real API calls to Todoist and require additional setup.
See [Integration Testing Guide](docs/integration-testing.md) for detailed instructions.

```bash
# Run integration tests
pytest tests/test_integration.py -m integration -v

# Run all tests (unit + integration)
pytest -v
```

**Important:** Integration tests:

- Require `TODOIST_API_TOKEN` environment variable
- Make real API calls and create/delete actual tasks
- Should use a dedicated test account and project
- Are not run in CI/CD (manual only)

For complete setup instructions, troubleshooting, and best practices, see the [Integration Testing Guide](docs/integration-testing.md).

### Code Quality

[rest of existing content...]

```markdown

**Testing:**

```bash
# Verify markdown formatting
markdownlint README.md

# Check links work
grep -A2 "Integration Testing" README.md
```

### Step 4: Verify Documentation Quality

**Review checklist:**

- [ ] All links work and point to correct locations
- [ ] Markdown formatting is correct
- [ ] Code blocks have proper syntax highlighting
- [ ] Safety warnings are prominent and clear
- [ ] Step-by-step instructions are easy to follow
- [ ] Example commands are copy-pasteable
- [ ] Troubleshooting covers common issues from experience
- [ ] Example output matches actual test runs

**Testing:**

```bash
# Run markdownlint on all changed files
pre-commit run markdownlint --files docs/integration-testing.md README.md

# Manually verify all links
# Check that docs/integration-testing.md exists
# Verify relative links work

# Test the documented commands
pytest tests/test_integration.py -m integration -v --co
```

### Step 5: Commit Documentation Changes

**Files modified:**

1. `docs/integration-testing.md` (new)
2. `.env.example` (updated)
3. `README.md` (updated)

**Commit message:**

```bash
git add docs/integration-testing.md .env.example README.md
git commit -m "$(cat <<'EOF'
docs: add comprehensive integration testing documentation

Add detailed guide for running integration tests against real Todoist API:
- Created docs/integration-testing.md with complete setup instructions
- Updated .env.example to include integration test variables
- Added Integration Testing section to README.md with link to guide

Documentation includes:
- Prerequisites and API token setup
- Safety guidelines for using test accounts
- Environment variable configuration
- Running tests with pytest commands
- Troubleshooting common API issues
- Best practices for integration testing

Closes #9

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

## Testing Strategy

### Documentation Quality Testing

**Test Case 1: Follow the Documentation**

1. Create a new test Todoist account
2. Follow docs/integration-testing.md step-by-step
3. Verify each step works as documented
4. Note any missing steps or unclear instructions

**Expected result:**

- Successfully set up integration tests
- All commands work as documented
- No confusion or missing information

**Test Case 2: Verify Links**

1. Open README.md in GitHub preview
2. Click "Integration Testing Guide" link
3. Verify it navigates to docs/integration-testing.md

**Expected result:**

- Link works correctly
- Documentation renders properly

**Test Case 3: Run Documented Commands**

1. Copy each command from the documentation
2. Paste and run in terminal
3. Verify output matches expectations

**Expected result:**

- All commands are correct and executable
- No syntax errors or typos

### Markdown Formatting Validation

```bash
# Run pre-commit hooks
pre-commit run markdownlint --files docs/integration-testing.md README.md

# Check for common issues
grep -n "http://" docs/integration-testing.md  # Should use https
grep -n "TODO\|FIXME" docs/integration-testing.md  # Should be none
```

**Expected result:**

- No markdown linting errors
- All URLs use HTTPS
- No placeholder TODOs

### Content Completeness Check

**Verify documentation includes:**

- [ ] Overview of integration testing
- [ ] Prerequisites section
- [ ] API token retrieval instructions
- [ ] Test project creation guide
- [ ] Environment variable documentation
- [ ] Safety guidelines (prominent warnings)
- [ ] Commands to run tests
- [ ] What's tested (coverage overview)
- [ ] Troubleshooting section with 4+ common issues
- [ ] Example output
- [ ] CI/CD considerations
- [ ] Best practices list

## Success Criteria

- [x] `docs/integration-testing.md` created with comprehensive guide
- [x] Documentation includes step-by-step setup instructions
- [x] Safety guidelines prominently featured
- [x] Troubleshooting section covers common issues
- [x] `.env.example` updated with integration test variables
- [x] README.md links to integration testing documentation
- [x] All markdown passes linting (pre-commit hooks)
- [x] Links verified to work correctly
- [x] Code examples are copy-pasteable
- [x] Example output included for reference
- [x] Best practices documented

## Files Modified

1. `docs/integration-testing.md` (new) - Comprehensive integration testing guide
2. `.env.example` - Add integration test environment variables with comments
3. `README.md` - Add Integration Testing section with link to detailed guide

## Related Issues and Tasks

### Depends On

- None (documentation task, no dependencies)

### Blocks

- None (nice-to-have documentation improvement)

### Related

- Issue #4 - Add proper unit tests (complementary testing documentation)
- Issue #6 - Add CI workflow (explains why integration tests not in CI)

### Enables

- Better developer onboarding for integration testing
- Safer integration test execution with documented best practices
- Easier troubleshooting of integration test issues

## References

- [GitHub Issue #9](https://github.com/denhamparry/todoist-mcp/issues/9)
- [Todoist API Documentation](https://developer.todoist.com/rest/v2/)
- [Todoist API Token Guide](https://todoist.com/help/articles/find-your-api-token-Jpzx9IIlB)
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)

## Notes

### Key Insights

1. **Safety first** - Integration tests work with real API, so documentation must emphasize using dedicated test accounts and projects
2. **Developer experience** - Clear step-by-step instructions reduce friction and encourage proper test practices
3. **Troubleshooting** - API-related issues are common, so comprehensive troubleshooting section is critical
4. **CI exclusion** - Important to explain why integration tests aren't in CI (credentials, API load)

### Alternative Approaches Considered

1. **Embed in README.md** - Keep all documentation in README ❌
   - **Why not:** README is already long, integration testing deserves dedicated documentation

2. **Minimal documentation** - Just add environment variables to .env.example ❌
   - **Why not:** Insufficient for safety and proper usage

3. **Separate docs with link (chosen approach)** ✅
   - **Why chosen:**
     - Detailed documentation without cluttering README
     - Easy to find via README link
     - Can be comprehensive without overwhelming main docs
     - Follows existing docs/ structure pattern

### Development Best Practices

1. **Safety warnings** - Use emoji (⚠️) and bold text for critical safety information
2. **Code examples** - All commands should be copy-pasteable
3. **Troubleshooting** - Include actual error messages and specific solutions
4. **Links** - Provide direct links to external resources (Todoist help, API docs)
5. **Example output** - Show what success looks like so users can verify

### Documentation Standards

- Use clear headings and hierarchy
- Include code syntax highlighting
- Provide context before commands
- Explain why, not just what
- Link to related documentation
- Keep security considerations prominent
