# Pre-commit Hooks Configuration

## Overview

This project uses **pre-commit** hooks to maintain code quality and consistency across the codebase. The hooks automatically run before each commit to catch issues early.

## What's Included

### Python (Backend)

1. **Ruff** - Fast Python linter and formatter
   - Replaces: black, isort, flake8, pyupgrade
   - Checks: code style, imports, complexity, bugs
   - Auto-fixes: import sorting, code formatting

2. **MyPy** - Static type checker
   - Validates type hints
   - Catches type-related bugs early
   - Configured for Python 3.10+

3. **PyUpgrade** - Modernizes Python syntax
   - Upgrades to Python 3.10+ syntax
   - Removes outdated patterns

### TypeScript/JavaScript (Frontend)

1. **ESLint** - JavaScript/TypeScript linter
   - Next.js configuration
   - Auto-fixes common issues

### General

1. **File Cleanup**
   - Removes trailing whitespace
   - Ensures files end with newline
   - Checks for merge conflicts
   - Prevents large files (>1MB)

2. **Format Validation**
   - YAML syntax checking
   - TOML syntax checking
   - JSON formatting

## Installation

```bash
# Navigate to backend directory
cd backend

# Install pre-commit hooks
poetry run pre-commit install

# This will install hooks in .git/hooks/pre-commit
```

## Usage

### Automatic (Recommended)

Once installed, hooks run automatically before each commit:

```bash
git add .
git commit -m "feat: add new feature"
# Pre-commit hooks will run automatically
```

If hooks fail:
- Review the output
- Fix the issues (many are auto-fixed)
- Stage the changes again
- Retry the commit

### Manual

Run hooks manually on all files:

```bash
cd backend
poetry run pre-commit run --all-files
```

Run specific hook:

```bash
poetry run pre-commit run ruff --all-files
poetry run pre-commit run mypy --all-files
```

## Configuration

### Pre-commit Config

File: `.pre-commit-config.yaml` (project root)

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.15
    hooks:
      - id: ruff
        args: [--fix, --config=backend/pyproject.toml]
      - id: ruff-format
```

### Ruff Config

File: `backend/pyproject.toml`

```toml
[tool.ruff]
target-version = "py310"
line-length = 100

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP"]
ignore = ["E501", "B008", "C901"]
```

### MyPy Config

File: `backend/pyproject.toml`

```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
check_untyped_defs = true
ignore_missing_imports = true
```

## Skipping Hooks (Emergency Only)

If you absolutely need to skip hooks:

```bash
git commit --no-verify -m "emergency fix"
```

**⚠️ Warning:** Only use this in emergencies. Skipping hooks can introduce code quality issues.

## Updating Hooks

Pre-commit hooks auto-update weekly (configured in `.pre-commit-config.yaml`).

Manual update:

```bash
cd backend
poetry run pre-commit autoupdate
```

## Troubleshooting

### Hooks Not Running

```bash
# Reinstall hooks
cd backend
poetry run pre-commit uninstall
poetry run pre-commit install
```

### Ruff Errors

```bash
# Run ruff manually to see detailed errors
cd backend
poetry run ruff check .

# Auto-fix issues
poetry run ruff check --fix .
```

### MyPy Errors

```bash
# Run mypy manually
cd backend
poetry run mypy app/

# Ignore specific errors (add to pyproject.toml)
# type: ignore
```

### Slow Pre-commit

First run is slow (installing environments). Subsequent runs are fast.

To speed up:
```bash
# Run hooks in parallel (default)
# Already configured in .pre-commit-config.yaml
```

## What Gets Checked

### Before Every Commit

✅ **Automatically Fixed:**
- Trailing whitespace removed
- File endings normalized
- Imports sorted
- Code formatted (ruff)
- JSON formatted

⚠️ **Requires Manual Fix:**
- Type errors (mypy)
- Syntax errors
- Merge conflicts
- Large files

### Example Output

```bash
$ git commit -m "feat: add chat service"

Trim trailing whitespace.........................Passed
Fix end of files.................................Passed
Check YAML syntax................................Passed
Ruff linter......................................Passed
Ruff formatter...................................Passed
Type check with mypy.............................Failed
- hook id: mypy
- exit code: 1

app/services/chat_service.py:15: error: Function is missing a return type annotation

# Fix the error, stage changes, and retry
```

## Best Practices

1. **Run hooks before pushing:**
   ```bash
   poetry run pre-commit run --all-files
   ```

2. **Fix issues incrementally:**
   - Don't accumulate many changes
   - Commit frequently
   - Let hooks catch issues early

3. **Understand the errors:**
   - Read the hook output
   - Learn from the suggestions
   - Improve code quality over time

4. **Keep hooks updated:**
   - Auto-update is enabled
   - Review updates in PRs
   - Test after updates

## CI/CD Integration

Pre-commit hooks also run in CI/CD pipelines (when configured).

This ensures:
- Code quality on all branches
- Consistent standards across team
- Early detection of issues

## Additional Resources

- [Pre-commit Documentation](https://pre-commit.com/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [ESLint Documentation](https://eslint.org/)
