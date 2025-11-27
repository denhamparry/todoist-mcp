# GitHub Issue #6: Add CI workflow to verify tests and coverage

**Issue:** [#6](https://github.com/denhamparry/todoist-mcp/issues/6)
**Status:** Open
**Priority:** HIGH
**Date:** 2025-11-27

## Problem Statement

The project currently lacks automated continuous integration (CI) to verify code quality, run tests, and enforce coverage standards on pull requests and commits. While there is a placeholder `.github/workflows/ci.yml` file, it only contains commented-out template code and doesn't perform any actual verification.

### Current Behavior

- `.github/workflows/ci.yml` exists but only contains placeholder comments
- No automated testing on PRs or commits to main branch
- No enforcement of code quality standards (black, isort, flake8, mypy)
- No coverage verification (project requires >80% coverage per pyproject.toml:36)
- No CI status badge in README
- Pre-commit hooks exist but aren't verified in CI

### Expected Behavior

- CI workflow runs automatically on all PRs and commits to main
- Tests execute on Python 3.10, 3.11, and 3.12 with matrix strategy
- Coverage enforced at >80% threshold
- Code quality checks pass (black, isort, flake8, mypy)
- Pre-commit hooks verified in CI
- README displays CI status badge showing build status

## Current State Analysis

### Relevant Configuration Files

**`.github/workflows/ci.yml`** (Lines 1-63)

- Contains only placeholder template code
- All job definitions are commented out
- Single placeholder job that echoes a message

**`pyproject.toml`** (Lines 1-43)

- Python version requirement: `>=3.10`
- Dev dependencies already configured:
  - pytest 8.0.0+
  - pytest-asyncio 0.23.0+
  - pytest-cov 4.1.0+
  - pytest-httpx 0.30.0+
  - black 24.0.0+
  - isort 5.13.0+
  - flake8 7.0.0+
  - mypy 1.11.0+
- Pytest configuration (lines 32-36):
  - Test path: `tests/`
  - Coverage target: `src/todoist_mcp`
  - Coverage threshold: `--cov-fail-under=80`
  - Report format: `--cov-report=term-missing`

**`.pre-commit-config.yaml`** (Lines 1-67)

- Already configured with Python formatting/linting hooks
- black, isort, flake8, mypy hooks defined
- Also includes general file quality and secret detection hooks

**`README.md`**

- No CI status badge currently present
- Has Development section (lines 145-172) documenting test commands

### Test Infrastructure

- Test directory exists: `tests/`
- Test files present:
  - `tests/conftest.py` - Pytest fixtures
  - `tests/test_server.py` - Unit tests
  - `tests/test_integration.py` - Integration tests

### Related Context

- Project uses setuptools build system
- Main entry point: `todoist_mcp.server:main`
- Tests use asyncio mode (pytest-asyncio)
- pre-commit hooks already configured

## Solution Design

### Approach

Replace the placeholder CI workflow with a fully functional multi-job workflow that:

1. **Tests Job**: Run pytest on multiple Python versions with coverage reporting
2. **Code Quality Job**: Verify formatting and linting standards
3. **Pre-commit Job**: Ensure pre-commit hooks pass

This approach follows best practices:

- Matrix testing across Python versions ensures compatibility
- Separate jobs for testing and code quality allow parallel execution
- Fail-fast strategy catches issues early
- Reuses existing tool configurations from pyproject.toml and .pre-commit-config.yaml

### Implementation

Replace `.github/workflows/ci.yml` with the following structure:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    name: Test (Python ${{ matrix.python-version }})
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
      fail-fast: false
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Run tests with coverage
        run: |
          pytest --cov=src/todoist_mcp --cov-report=term-missing --cov-report=xml --cov-fail-under=80

      - name: Upload coverage reports
        if: matrix.python-version == '3.12'
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: false

  code-quality:
    name: Code Quality
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Check formatting with black
        run: black --check src/ tests/

      - name: Check import sorting with isort
        run: isort --check-only --profile black src/ tests/

      - name: Lint with flake8
        run: flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203

      - name: Type check with mypy
        run: mypy src/ --ignore-missing-imports

  pre-commit:
    name: Pre-commit Hooks
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install pre-commit
        run: pip install pre-commit

      - name: Run pre-commit hooks
        run: pre-commit run --all-files
```

Add status badge to README.md after the title:

```markdown
# Todoist MCP Server

[![CI](https://github.com/denhamparry/todoist-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/denhamparry/todoist-mcp/actions/workflows/ci.yml)
```

### Benefits

- **Automated Quality Gates**: Every PR and commit automatically verified
- **Multi-version Testing**: Ensures compatibility with Python 3.10, 3.11, 3.12
- **Coverage Enforcement**: Prevents merging code that drops below 80% coverage
- **Fast Feedback**: Parallel jobs provide quick feedback to developers
- **Visual Status**: Badge shows build status at a glance
- **Consistency**: CI uses same tools/configs as local development
- **Pre-commit Verification**: Catches issues that developers might skip locally

## Implementation Plan

### Step 1: Update CI Workflow

**File:** `.github/workflows/ci.yml`

**Changes:**

- Remove placeholder job (lines 57-62)
- Uncomment and replace template with production-ready workflow
- Add three jobs: `test`, `code-quality`, `pre-commit`
- Configure test matrix for Python 3.10, 3.11, 3.12
- Add coverage upload to Codecov (optional but recommended)

**Testing:**

```bash
# Validate YAML syntax
yamllint .github/workflows/ci.yml

# Test locally (if act is installed)
act pull_request
```

### Step 2: Add CI Status Badge

**File:** `README.md`

**Changes:**

- Insert badge after line 1 (after main title)
- Badge format: `[![CI](badge-url)](workflow-url)`
- Update badge URL to use correct repository path

**Testing:**

```bash
# Verify markdown renders correctly
cat README.md | head -5
```

### Step 3: Verify Workflow Configuration

**Files:** `pyproject.toml`, `.pre-commit-config.yaml`

**Verification:**

- Confirm pytest coverage settings match CI (line 36)
- Confirm tool versions match between pre-commit config and dev dependencies
- Verify flake8 args in CI match local config expectations

**Testing:**

```bash
# Run tools locally to ensure they work
pytest
black --check src/ tests/
isort --check-only --profile black src/ tests/
flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203
mypy src/ --ignore-missing-imports
pre-commit run --all-files
```

### Step 4: Test CI Workflow

**Actions:**

1. Push changes to feature branch
2. Create pull request
3. Verify all three jobs execute successfully
4. Check that matrix testing shows results for all Python versions
5. Verify coverage report is generated
6. Confirm pre-commit hooks pass
7. Check that badge appears in README

**Testing:**

```bash
# Push to trigger CI
git add .github/workflows/ci.yml README.md
git commit -m "feat: add CI workflow for tests and coverage"
git push origin <branch-name>

# Monitor workflow
gh run watch
```

### Step 5: Document CI Workflow

**File:** `README.md` (Development section)

**Changes:**

- Add note about CI workflow in Development section (around line 145)
- Mention that CI runs same checks as local development
- Reference that PR status must be green before merge

**Example addition:**

```markdown
### Continuous Integration

All pull requests run automated CI checks:
- Tests on Python 3.10, 3.11, 3.12
- Code coverage (must be >80%)
- Code quality (black, isort, flake8, mypy)
- Pre-commit hooks verification

CI uses the same configurations as local development, so running pre-commit
hooks and tests locally should match CI results.
```

## Testing Strategy

### Unit Testing

- **Existing tests should pass**: All tests in `tests/test_server.py` and `tests/test_integration.py` must pass
- **Coverage threshold**: Pytest will fail if coverage drops below 80%
- **Multi-version compatibility**: Tests run on Python 3.10, 3.11, 3.12

### Integration Testing

**Test Case 1: Pull Request Workflow**

1. Create feature branch
2. Make code change
3. Create pull request
4. Verify CI triggers automatically
5. Check all jobs complete successfully
6. Verify status badge updates

**Expected Result:** All CI jobs pass, PR shows green checkmarks

**Test Case 2: Failing Test Detection**

1. Intentionally break a test
2. Push to PR branch
3. Verify CI fails on test job
4. Check that other jobs still run

**Expected Result:** Test job fails, PR blocked from merge

**Test Case 3: Coverage Enforcement**

1. Remove tests to drop coverage below 80%
2. Push to PR branch
3. Verify CI fails with coverage error

**Expected Result:** Test job fails with "coverage < 80%" message

**Test Case 4: Code Quality Violations**

1. Add unformatted code (black/isort violations)
2. Push to PR branch
3. Verify code-quality job fails

**Expected Result:** Code-quality job fails, shows formatting issues

### Regression Testing

- **Existing functionality preserved**: All current tests continue to pass
- **Manual test commands still work**: Local pytest, black, isort, etc. unchanged
- **Pre-commit hooks unaffected**: Hooks continue to work locally as before
- **README accuracy**: Documentation matches actual CI behavior

### Edge Cases

- **First run on empty branch**: CI should handle initial workflow execution
- **Concurrent PRs**: Multiple PRs should trigger separate CI runs
- **Force push to PR**: CI should re-run with latest commits
- **Draft PRs**: CI should still run (GitHub default behavior)

## Success Criteria

- [x] `.github/workflows/ci.yml` contains fully functional workflow (not placeholder)
- [x] CI triggers on pull requests to main branch
- [x] CI triggers on pushes to main branch
- [x] Tests run successfully on Python 3.10
- [x] Tests run successfully on Python 3.11
- [x] Tests run successfully on Python 3.12
- [x] Coverage check enforces >80% threshold
- [x] Black formatting check passes
- [x] Isort import sorting check passes
- [x] Flake8 linting check passes
- [x] Mypy type checking passes
- [x] Pre-commit hooks verification passes
- [x] CI status badge added to README.md
- [x] Badge displays correct build status (passing/failing)
- [x] All CI jobs complete within reasonable time (<5 minutes)
- [x] Workflow uses latest stable GitHub Actions versions

## Files Modified

1. `.github/workflows/ci.yml` - Complete rewrite from placeholder to production workflow
2. `README.md` - Add CI status badge after title

## Related Issues and Tasks

### Depends On

- None (all dependencies already satisfied)
- Dev dependencies already in pyproject.toml
- Pre-commit config already exists
- Tests already exist

### Blocks

- Future: Code quality improvements that require CI enforcement
- Future: Additional checks (security scanning, dependency audits)

### Related

- Pre-commit hooks configuration (`.pre-commit-config.yaml`)
- Test configuration (`pyproject.toml` pytest settings)
- Existing test suite (`tests/`)

### Enables

- Automated quality enforcement on all PRs
- Confidence in multi-version Python compatibility
- Protection against coverage regression
- Visible build status for contributors
- Foundation for additional CI jobs (security scans, etc.)

## References

- [GitHub Issue #6](https://github.com/denhamparry/todoist-mcp/issues/6)
- [GitHub Actions - Python](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [GitHub Actions - workflow syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Codecov GitHub Action](https://github.com/codecov/codecov-action)

## Notes

### Key Insights

1. **Existing configuration is complete**: All tool configs already exist in pyproject.toml and .pre-commit-config.yaml
2. **Only workflow needs implementation**: No changes needed to test infrastructure or tooling
3. **Parallel jobs for speed**: Separating code-quality from tests allows parallel execution
4. **Matrix strategy benefits**: Testing on 3 Python versions catches compatibility issues early
5. **Consistency with local dev**: CI should mirror local development commands exactly

### Alternative Approaches Considered

1. **Single job with all steps** - Simpler but slower, no parallelization ❌
2. **Tox for multi-version testing** - Adds complexity, GitHub Actions matrix is simpler ✅
3. **Separate workflow files** - Over-engineering for this project size ❌
4. **Include linting in pre-commit job only** - Less clear separation of concerns ❌
5. **Three separate jobs (chosen approach)** - Clear separation, parallel execution, easy to debug ✅

### Best Practices

- **Use latest action versions**: `@v4` for checkout, `@v5` for setup-python
- **Cache dependencies**: Consider adding pip cache for faster runs (future optimization)
- **Fail-fast: false**: Allow all Python versions to complete even if one fails
- **Coverage upload conditions**: Only upload from one Python version to avoid duplication
- **Badge placement**: Immediately after title for maximum visibility
- **Job names**: Descriptive names that appear in PR status checks

### Monitoring Approach

After implementation:

1. Monitor first few PR runs for timing and reliability
2. Check if jobs complete within expected timeframe (<5 minutes)
3. Verify matrix strategy properly tests all Python versions
4. Confirm coverage reports are accurate
5. Watch for any flaky tests that pass locally but fail in CI

### Future Enhancements

Potential additions (not in scope for this issue):

- Dependency caching to speed up workflow
- Parallel test execution with pytest-xdist
- Security scanning (bandit, safety)
- Dependency vulnerability scanning (Dependabot, Snyk)
- Performance benchmarking
- Documentation building/validation
- Release automation
