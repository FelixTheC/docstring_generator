# CLI Options

## `--style` — Choose your docstring convention

| Style | Flag | Description |
|-------|------|-------------|
| NumPy | `--style numpy` | Standard in scientific Python (default) |
| Google | `--style google` | Preferred in many enterprise codebases |
| reStructuredText | `--style rest` | Compatible with Sphinx auto-documentation |

**Default:** `numpy`

---

## `--check` — Docstring coverage report

Scan a file or directory and get a coverage overview without modifying anything:

```shell
gendocs_new mydir/ --check
```

Outputs a per-file summary showing which functions are documented and which are missing docstrings.

---

## `--strict` — Treat partial docstrings as missing

By default, a function with any docstring counts as documented. Strict mode raises the bar:

```shell
gendocs_new mydir/ --check --strict
```

A partial docstring (e.g. missing parameter sections) is treated as undocumented in strict mode.

---

## `--threshold` — Enforce a minimum coverage percentage

Fail the check if coverage drops below a given percentage (0–100):

```shell
gendocs_new mydir/ --check --threshold 80
```

Useful in CI pipelines to enforce documentation standards across the codebase.

---

## `--exclude-file` — Skip specific files

Exclude one or more files from processing by name. Can be passed multiple times:

```shell
gendocs_new mydir/ --exclude-file conftest.py --exclude-file settings.py
```

Files whose name matches any of the provided values are skipped during docstring generation.

---

## `--exclude-dir` — Skip specific directories

Exclude one or more directories from processing. Can be passed multiple times:

```shell
gendocs_new mydir/ --exclude-dir tests --exclude-dir migrations
```

Any file whose path contains one of the given directory names is skipped.

---

## `--dry-run` — Preview changes without modifying any file

Run the generator in read-only mode and see exactly what would be added or changed as a unified diff:

```shell
gendocs_new mydir/ --dry-run
```

Files that already have complete docstrings print `<file>: no changes`. Files with missing docstrings show a `+`/`-` diff so you can review before committing. Combine with `--style` or `--overwrite-style` to preview a style migration:

```shell
gendocs_new mydir/ --style google --overwrite-style --dry-run
```

---

## `--changed-only` — Only process git-changed files

Restrict processing to files that are modified or staged in git — perfect for large repos where running on the full `src/` directory on every commit would be slow:

```shell
gendocs_new mydir/ --changed-only
```

Internally runs `git diff --name-only HEAD` and `git diff --cached --name-only` to collect the list of changed and staged `.py` files, then intersects that list with the paths you provided. If git is not installed or not available on `PATH`, the command aborts immediately with a clear error message rather than silently processing everything.

Combines well with `--dry-run` to preview what *would* change for only the files you touched:

```shell
gendocs_new mydir/ --changed-only --dry-run
```

---

## `--ignore-magic` — Skip dunder / magic methods

Exclude dunder methods such as `__init__`, `__str__`, `__repr__`, `__eq__`, etc. from docstring generation:

```shell
gendocs_new mydir/ --ignore-magic
```

Can also be enabled permanently via `pyproject.toml` so every invocation skips magic methods without an explicit flag:

```toml
[tool.docstring_generator]
ignore_magic = true
```

---

## `--overwrite-style` — Re-format existing docstrings in a different style

Force regeneration of existing docstrings using the specified style, even if they already have content:

```shell
gendocs_new mydir/ --style google --overwrite-style true
```

Useful when migrating a codebase from one docstring convention to another.

---

## `--ignore-private` — Skip private functions/methods

Skip functions and methods whose name starts with a single underscore (e.g. `_helper`), leaving them untouched. Dunder methods (e.g. `__init__`, `__str__`) are **not** affected by this flag — use `--ignore-magic` for those:

```shell
gendocs_new mydir/ --ignore-private
```

Can also be enabled permanently via `pyproject.toml`:

```toml
[tool.docstring_generator]
ignore_private = true
```

**Default:** `False`

---

## `--ignore-uncommented` — Skip functions without an existing docstring

Skip functions and methods that currently have **no docstring at all**, leaving them untouched instead of generating one. This is useful for simple helper functions where the name is already self-explanatory and you don't want the tool to add boilerplate:

```shell
gendocs_new mydir/ --ignore-uncommented
```

Functions that already have *some* docstring are still processed normally (e.g. missing `Parameters`/`Returns` sections are added). Only fully undocumented functions are skipped.

Can also be enabled permanently via `pyproject.toml`:

```toml
[tool.docstring_generator]
ignore_uncommented = true
```

**Default:** `False`

---

## Skip Directives — `# docstring: skip` / `# docstring: off` / `# docstring: on`

Sometimes a flag is too coarse — you want to skip *specific* files, functions, or classes without changing how the rest of the codebase is processed. For that, `docstring_generator` supports inline comment directives. See the [Skip Directives](skip-directives.md) page for the full guide with examples for each of the three supported scopes (file-level, single-target, and block/range).
