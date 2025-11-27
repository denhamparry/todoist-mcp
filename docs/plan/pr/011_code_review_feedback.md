# PR #11: Code Review Feedback - Add comprehensive unit tests

**PR:** #11 **Status:** In Progress **Created:** 2025-11-27

## PR Summary

Implements comprehensive unit tests for all 7 MCP tools with properly mocked success scenarios, fixing Issue #4. Tests achieve **95.19% code coverage** and discovered/fixed 5 critical bugs.

## Review Feedback from Claude Bot

**Review Date:** 2025-11-27T18:20:27Z
**Reviewer:** claude
**Overall Assessment:** APPROVE & MERGE (with minor improvement suggestions)

### Feedback Items

#### High Priority

No high priority blocking issues identified.

#### Medium Priority

1. **Inconsistent assertion styles**

   **Location:** `tests/test_server.py` (multiple locations)

   **Issue:** Tests use different assertion styles inconsistently:
   - Some use `assert "text" in result` (test_server.py:159)
   - Others use `assert result == "exact text"` (test_server.py:180)

   **Required Change:** Standardize on:
   - Use `assert "text" in result` for partial matches
   - Use `assert result == "exact text"` for exact matches

2. **Duplicate test logic**

   **Location:** `tests/test_server.py:184-201`

   **Issue:** Some tests manually create async generator mocks instead of using the helper function

   **Required Change:** Use `create_async_gen_mock()` consistently across all tests

3. **Magic numbers in priority mapping**

   **Location:** `src/todoist_mcp/server.py:58-61`

   **Issue:** Priority values (1, 2, 3, 4) and their meanings aren't documented

   **Required Change:** Add a comment explaining Todoist's priority system or extract to a constant

   ```python
   # Todoist priority mapping:
   # 1 = Normal (lowest), 2 = Medium, 3 = High, 4 = Urgent (highest)
   priority_map = {"low": 1, "medium": 2, "high": 3, "urgent": 4}
   ```

#### Low Priority

No low priority items identified.

## Implementation Plan

### 1. Standardize Test Assertions

- Review all test assertions in `tests/test_server.py`
- Ensure partial matches use `assert "text" in result`
- Ensure exact matches use `assert result == "exact text"`
- Update inconsistent assertions

### 2. Refactor Test Mocking

- Review tests that manually create async generator mocks
- Replace manual creation with `create_async_gen_mock()` helper
- Ensure consistency across all test functions

### 3. Document Priority Mapping

- Add comment explaining Todoist priority system
- Consider extracting to a constant if it improves readability
- Update the priority mapping in `todoist_create_task` and `todoist_update_task`

### 4. Verification

- Run full test suite
- Verify all tests still pass
- Run pre-commit hooks
- Commit changes

## Success Criteria

- [ ] All test assertions use consistent style
- [ ] All tests use `create_async_gen_mock()` helper consistently
- [ ] Priority mapping is documented with clear comments
- [ ] All tests pass (25/25)
- [ ] Coverage remains >= 95%
- [ ] Pre-commit hooks pass

## Related Files

- `tests/test_server.py` - Test assertions and mocking
- `src/todoist_mcp/server.py` - Priority mapping
- `tests/conftest.py` - Helper function reference

## Notes

This PR is already approved for merging. These improvements are code quality enhancements that don't block the merge but will improve maintainability and readability.
