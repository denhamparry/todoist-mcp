# PR #13: Add CI workflow for tests and coverage verification

**PR:** [#13](https://github.com/denhamparry/todoist-mcp/pull/13) **Status:**
Complete **Created:** 2025-11-27 **Updated:** 2025-11-27

## Code Review Feedback Summary

Comprehensive code review completed by Claude. The CI workflow implementation is
**well-structured and production-ready** with successful CI runs. One critical
issue and several enhancements identified.

**CI Status:** ✅ All jobs passing
([run #19747385916](https://github.com/denhamparry/todoist-mcp/actions/runs/19747385916))

---

## Feedback Items

### Critical Priority

#### 1. Mypy Target Directories Mismatch

**Location:** `.github/workflows/ci.yml:67`

**Issue:** The CI only type-checks `src/` directory, while the pre-commit hook
checks both source and tests. This creates inconsistency between local
pre-commit and CI environments.

**Current Code:**

```yaml
- name: Type check with mypy
  run: mypy src/ --ignore-missing-imports
```

**Pre-commit Configuration (.pre-commit-config.yaml:62-66):**

```yaml
- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v1.11.2
  hooks:
    - id: mypy
      name: Type check Python with mypy
      args: [--ignore-missing-imports]
```

The pre-commit hook runs on all Python files (including tests) by default.

**Impact:** Tests could have type issues that pass CI but fail pre-commit hooks
locally, causing confusion and workflow inconsistency.

**Required Change:**

```yaml
- name: Type check with mypy
  run: mypy src/ tests/ --ignore-missing-imports
```

---

### Medium Priority

#### 2. Missing Dependency Caching

**Location:** `.github/workflows/ci.yml` - all jobs

**Issue:** Dependencies are installed fresh on every CI run, which is slower and
uses more GitHub Actions minutes.

**Impact:**

- Slower CI runs (30-60 seconds overhead per job)
- Increased GitHub Actions minutes usage
- Unnecessary network traffic

**Recommended Enhancement:**

```yaml
- name: Set up Python ${{ matrix.python-version }}
  uses: actions/setup-python@v5
  with:
    python-version: ${{ matrix.python-version }}
    cache: "pip"
    cache-dependency-path: "pyproject.toml"
```

Apply to all three jobs (test, code-quality, pre-commit).

---

#### 3. Missing Coverage Report Artifacts

**Location:** `.github/workflows/ci.yml:34-39`

**Issue:** Coverage XML is only uploaded to Codecov (optional external service),
but not stored as GitHub Actions artifacts.

**Impact:**

- Coverage reports not accessible if Codecov is down or not configured
- No way to view coverage details directly in GitHub Actions UI
- Harder to debug coverage issues

**Recommended Enhancement:**

```yaml
- name: Upload coverage artifacts
  if: matrix.python-version == '3.12'
  uses: actions/upload-artifact@v4
  with:
    name: coverage-report
    path: |
      ./coverage.xml
      htmlcov/
```

---

### Low Priority (Documentation/Future)

#### 4. Tool Version Alignment

**Issue:** Pre-commit hooks use pinned versions while CI installs latest from
pyproject.toml dev dependencies.

**Examples:**

- Pre-commit black: `rev: 24.10.0` (pinned)
- CI installs: `black>=24.0.0` (latest)

**Potential Issue:** Version drift could cause different behavior between local
pre-commit and CI over time.

**Options:**

1. Pin exact versions in pyproject.toml: `black==24.10.0`
2. Use `pre-commit run --all-files` in CI instead of running tools separately
3. Document that version drift is acceptable and why

**Recommendation:** Document the current approach in CLAUDE.md or README to
explain the versioning strategy.

---

#### 5. Explicit Mypy Configuration

**Issue:** Mypy configuration is implicit in command-line arguments rather than
explicit in pyproject.toml.

**Recommendation:** Add explicit mypy configuration for consistency:

```toml
[tool.mypy]
ignore_missing_imports = true
files = ["src", "tests"]
```

This makes configuration version-controlled and explicit.

---

## Implementation Plan

### Step 1: Fix Critical Issue - Mypy Target Directories

**File:** `.github/workflows/ci.yml`

**Action:** Update line 67 in the code-quality job to include tests directory.

**Change:**

```yaml
# Before
run: mypy src/ --ignore-missing-imports

# After
run: mypy src/ tests/ --ignore-missing-imports
```

**Verification:** Run locally to ensure tests pass type checking:

```bash
mypy src/ tests/ --ignore-missing-imports
```

---

### Step 2: Add Dependency Caching (Medium Priority)

**Files:** `.github/workflows/ci.yml`

**Action:** Update all three Python setup steps to include pip caching.

**Jobs to update:**

1. test job (line ~20)
2. code-quality job (line ~47)
3. pre-commit job (line ~75)

**Change for each:**

```yaml
- name: Set up Python ${{ matrix.python-version }} # or "3.12" for non-matrix
  uses: actions/setup-python@v5
  with:
    python-version: ${{ matrix.python-version }} # or "3.12"
    cache: "pip"
    cache-dependency-path: "pyproject.toml"
```

---

### Step 3: Add Coverage Artifacts (Medium Priority)

**File:** `.github/workflows/ci.yml`

**Action:** Add artifact upload step after coverage upload in test job.

**Location:** After line 39 (after Codecov upload)

**Addition:**

```yaml
- name: Upload coverage artifacts
  if: matrix.python-version == '3.12'
  uses: actions/upload-artifact@v4
  with:
    name: coverage-report
    path: |
      coverage.xml
      htmlcov/
```

Note: Need to update pytest command to also generate HTML coverage:

```yaml
run: |
  pytest --cov=src/todoist_mcp --cov-report=term-missing --cov-report=xml --cov-report=html --cov-fail-under=80
```

---

### Step 4: Update Plan Document

**File:** `docs/plan/issues/6_add_ci_workflow_to_verify_tests_and_coverage.md`

**Action:** Add note about PR feedback and implementation.

---

### Step 5: Testing

**Local verification:**

```bash
# Verify mypy works with both directories
mypy src/ tests/ --ignore-missing-imports

# Verify YAML syntax
python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"

# Run pre-commit hooks
pre-commit run --all-files
```

**CI verification:**

- Push changes and verify CI runs successfully
- Check that caching is working (subsequent runs faster)
- Verify coverage artifacts are uploaded

---

## Testing Strategy

### Unit Testing

- No new code to test (only CI configuration changes)
- Existing tests must continue to pass
- Mypy type checking must pass for both src/ and tests/

### Integration Testing

- **Test Case 1:** Push changes and verify CI triggers
- **Test Case 2:** Verify all three jobs complete successfully
- **Test Case 3:** Check dependency caching works (view cache in Actions UI)
- **Test Case 4:** Verify coverage artifacts are downloadable

### Verification Commands

```bash
# Local mypy check
mypy src/ tests/ --ignore-missing-imports

# Pre-commit
pre-commit run --all-files

# View CI run
gh run watch
```

---

## Success Criteria

- [ ] Mypy checks both src/ and tests/ directories in CI
- [ ] Dependency caching configured for all three jobs
- [ ] Coverage artifacts uploaded to GitHub Actions
- [ ] All CI jobs continue to pass
- [ ] Pre-commit hooks pass
- [ ] No regression in CI run time (should be faster with caching)
- [ ] Coverage reports accessible as artifacts

---

## Files to Modify

1. `.github/workflows/ci.yml` - Update mypy, add caching, add artifacts
2. `docs/plan/issues/6_add_ci_workflow_to_verify_tests_and_coverage.md` - Note
   PR feedback

---

## Related Issues

- Resolves feedback from PR #13 code review
- Improves on issue #6 implementation
- Enhances CI reliability and performance

---

## References

- [PR #13 Code Review Comment](https://github.com/denhamparry/todoist-mcp/pull/13#issuecomment-3587222960)
- [GitHub Actions Caching](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
- [GitHub Actions Artifacts](https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts)
- [setup-python caching](https://github.com/actions/setup-python#caching-packages-dependencies)

---

## Notes

### Code Review Highlights

**Strengths identified:**

- ✅ Excellent job parallelization
- ✅ Comprehensive Python version coverage (3.10-3.12)
- ✅ Proper coverage configuration
- ✅ Smart Codecov upload (only from 3.12)
- ✅ Code quality consistency with pre-commit
- ✅ Clean README badge integration

**Security:** No issues identified

**Current CI Status:** All checks passing successfully

### Implementation Priority

1. **Must Fix (Critical):** Mypy directory mismatch - creates workflow
   inconsistency
2. **Should Add (Medium):** Dependency caching - improves performance
3. **Should Add (Medium):** Coverage artifacts - improves debugging
4. **Nice to Have (Low):** Documentation improvements

### Decision Log

- **Mypy directories:** Decided to add tests/ to match pre-commit behavior
- **Caching strategy:** Using setup-python's built-in cache feature for
  simplicity
- **Coverage artifacts:** Including both XML and HTML for comprehensive
  debugging
