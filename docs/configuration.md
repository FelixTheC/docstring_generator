# Configuration via `pyproject.toml`

Instead of passing flags on every invocation, persist defaults in your project's `pyproject.toml` under the `[tool.docstring_generator]` namespace:

```toml
[tool.docstring_generator]
strict = true
threshold = 90
exclude_files = ["conftest.py", "settings.py"]
exclude_dirs = ["tests", "migrations"]
ignore_magic = true
```

CLI flags always override `pyproject.toml` values. The tool automatically walks up from the target path to find the nearest `pyproject.toml`.

## Available Keys

| Key | Type | CLI equivalent | Description |
|-----|------|----------------|-------------|
| `strict` | bool | `--strict` | Treat partial docstrings as missing |
| `threshold` | int (0–100) | `--threshold` | Minimum coverage percentage |
| `exclude_files` | list of str | `--exclude-file` | File names to skip |
| `exclude_dirs` | list of str | `--exclude-dir` | Directory names to skip |
| `ignore_magic` | bool | `--ignore-magic` | Skip dunder/magic methods |
