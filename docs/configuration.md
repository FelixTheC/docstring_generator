# Configuration via `pyproject.toml`

Instead of passing flags on every invocation, persist defaults in your project's `pyproject.toml` under the `[tool.docstring_generator]` namespace:

```toml
[tool.docstring_generator]
strict = true
threshold = 90
exclude_files = ["conftest.py", "settings.py"]
exclude_dirs = ["tests", "migrations"]
ignore_magic = true
ignore_private = true
ignore_uncommented = true
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
| `ignore_private` | bool | `--ignore-private` | Skip functions/methods whose name starts with a single underscore (dunder methods are unaffected) |
| `ignore_uncommented` | bool | `--ignore-uncommented` | Skip functions/methods that currently have no docstring at all |

> Looking for the `# docstring: skip` / `# docstring: off` / `# docstring: on` comment directives? Those aren't configured via `pyproject.toml` — see the [Skip Directives](skip-directives.md) page.
