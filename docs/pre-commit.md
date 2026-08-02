# Pre-commit Integration

Automatically generate docstrings on every commit using the [pre-commit](https://pre-commit.com/) framework.

## Setup

Add this to your project's `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/FelixTheC/docstring_generator
    rev: v0.3.4          # pin to a release tag
    hooks:
      - id: gendocs
        args: [src/]     # directory to process
```

Install the hook:

```shell
pip install pre-commit
pre-commit install
```

## How it works

The hook runs `gendocs_new` before each commit. If it generates or updates any docstrings, the commit is intentionally stopped so you can review and stage the changes:

| Run | What happens | Status |
|-----|-------------|--------|
| 1st commit | Hook generates docstrings → files modified | ❌ Stopped (intentional) |
| `git add` modified files | Stage the generated docstrings | — |
| 2nd commit | Hook runs, nothing changed | ✅ Passed |

This is standard behavior for any auto-fix hook (same as Black or isort).

## Customizing the style

```yaml
hooks:
  - id: gendocs
    args: [src/, --style, google]
```
