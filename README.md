[![Python 3.10](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/docstring-generator.svg)](https://badge.fury.io/py/docstring-generator)
![Actions](https://github.com/FelixTheC/docstring_generator/actions/workflows/python-app.yml/badge.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![](https://img.shields.io/pypi/dm/docstring-generator.svg)](https://pypi.org/project/docstring-generator/)
[![VS Code Extension](https://img.shields.io/badge/VS%20Code-Extension-007ACC?logo=visualstudiocode&logoColor=white)](https://marketplace.visualstudio.com/items?itemName=felixthec.docstring-generator-vscode)
[![JetBrains File Watcher](https://img.shields.io/badge/JetBrains-File%20Watcher-000000?logo=jetbrains&logoColor=white)](gendocs_file_watchers.xml)

# docstring_generator

> **Stop writing boilerplate docstrings by hand.** `docstring_generator` reads your type hints and generates professional, standards-compliant documentation in seconds — keeping your codebase clean, consistent, and AI-ready.

Python documentation tooling that automatically generates docstrings for functions and class methods from their type hints, with full support for **NumPy**, **Google**, and **reStructuredText** styles.

---

## Why docstring_generator?

Good documentation is no longer optional. AI coding assistants, static analysis tools, and auto-generated API docs all depend on structured, accurate docstrings. Yet writing them by hand is tedious, error-prone, and rarely kept up-to-date.

`docstring_generator` solves this by:

- ⚡ **Saving hours** — generate docs for an entire codebase in one command
- 🔄 **Staying in sync** — re-running only updates what changed in the function signature
- ✍️ **Preserving your words** — existing descriptions and custom notes are never overwritten
- 🧠 **AI-workflow friendly** — well-structured docstrings improve context quality for LLM-assisted development
- 🚨 **Exception-aware** — automatically detects `raise` statements and documents them in a `Raises` section, so failure modes are part of your API contract
- 🙈 **Convention-correct** — `self` and `cls` are automatically excluded from generated parameter sections, matching every major docstring standard
- ⚙️ **Async-ready** — handles both `def` and `async def` functions transparently, no extra configuration needed
- 🎨 **Style-safe** — detects the existing docstring style and refuses to silently mix conventions; explicit opt-in required to convert styles
- 🏎️ **Blazing fast** — core engine written in C++ via [pybind11](https://github.com/FelixTheC/docstring_generator_ext)

---

## Quick Start

One command. Any file or directory:

```shell
pip install docstring-generator
```

```shell
gendocs_new file.py        # single file
gendocs_new mydir/         # entire directory
```

That's it. Your functions now have properly formatted docstrings.

> 💡 **Prefer working inside your editor?** Skip the terminal entirely — install the [VS Code extension](https://marketplace.visualstudio.com/items?itemName=felixthec.docstring-generator-vscode) or import the [JetBrains File Watcher](#jetbrains-ides-pycharm-intellij--python-plugin) to generate docstrings automatically every time you save a `.py` file. → [Jump to IDE Integration](#ide-integration)

---

## Options

### `--style` — Choose your docstring convention

| Style | Flag | Description |
|-------|------|-------------|
| NumPy | `--style numpy` | Standard in scientific Python (default) |
| Google | `--style google` | Preferred in many enterprise codebases |
| reStructuredText | `--style rest` | Compatible with Sphinx auto-documentation |

**Default:** `numpy`

### `--check` — Docstring coverage report

Scan a file or directory and get a coverage overview without modifying anything:

```shell
gendocs_new mydir/ --check
```

Outputs a per-file summary showing which functions are documented and which are missing docstrings.

### `--strict` — Treat partial docstrings as missing

By default, a function with any docstring counts as documented. Strict mode raises the bar:

```shell
gendocs_new mydir/ --check --strict
```

A partial docstring (e.g. missing parameter sections) is treated as undocumented in strict mode.

### `--threshold` — Enforce a minimum coverage percentage

Fail the check if coverage drops below a given percentage (0–100):

```shell
gendocs_new mydir/ --check --threshold 80
```

Useful in CI pipelines to enforce documentation standards across the codebase.

### `--exclude-file` — Skip specific files

Exclude one or more files from processing by name. Can be passed multiple times:

```shell
gendocs_new mydir/ --exclude-file conftest.py --exclude-file settings.py
```

Files whose name matches any of the provided values are skipped during docstring generation.

### `--exclude-dir` — Skip specific directories

Exclude one or more directories from processing. Can be passed multiple times:

```shell
gendocs_new mydir/ --exclude-dir tests --exclude-dir migrations
```

Any file whose path contains one of the given directory names is skipped.

### `--dry-run` — Preview changes without modifying any file

Run the generator in read-only mode and see exactly what would be added or changed as a unified diff:

```shell
gendocs_new mydir/ --dry-run
```

Files that already have complete docstrings print `<file>: no changes`. Files with missing docstrings show a `+`/`-` diff so you can review before committing. Combine with `--style` or `--overwrite-style` to preview a style migration:

```shell
gendocs_new mydir/ --style google --overwrite-style --dry-run
```

### `--changed-only` — Only process git-changed files

Restrict processing to files that are modified or staged in git — perfect for large repos where running on the full `src/` directory on every commit would be slow:

```shell
gendocs_new mydir/ --changed-only
```

Internally runs `git diff --name-only HEAD` and `git diff --cached --name-only` to collect the list of changed and staged `.py` files, then intersects that list with the paths you provided. If git is not installed or not available on `PATH`, the command aborts immediately with a clear error message rather than silently processing everything.

Combines well with `--dry-run` to preview what *would* change for only the files you touched:

```shell
gendocs_new mydir/ --changed-only --dry-run
```

### `--ignore-magic` — Skip dunder / magic methods

Exclude dunder methods such as `__init__`, `__str__`, `__repr__`, `__eq__`, etc. from docstring generation. These are often implementation details that add noise rather than value to public documentation:

```shell
gendocs_new mydir/ --ignore-magic
```

Can also be enabled permanently via `pyproject.toml` so every invocation skips magic methods without an explicit flag:

```toml
[tool.docstring_generator]
ignore_magic = true
```

### `--overwrite-style` — Re-format existing docstrings in a different style

Force regeneration of existing docstrings using the specified style, even if they already have content:

```shell
gendocs_new mydir/ --style google --overwrite-style true
```

Useful when migrating a codebase from one docstring convention to another.

---

## Configuration via `pyproject.toml`

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

---

## Preserve Custom Descriptions with `$<num>` Placeholders

Write your domain-specific notes once — `docstring_generator` will place them in the right parameter slot automatically.

Use `$1`, `$2`, … in your docstring body to map descriptions to positional parameters:

```python
from typing import List


def foo(val_a: int, val_b: List[int]):
    """
    Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
    sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam

    $1 Lorem ipsum dolor sit amet
    $2 nonumy eirmod tempor invidun
    """
```

After running `gendocs_new` (NumPy style):

```python
from typing import List


def foo(val_a: int, val_b: List[int]):
    """
    Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
    sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam

    Parameters
    ----------
    val_a : argument of type int
        Lorem ipsum dolor sit amet
    val_b : argument of type List(int)
        nonumy eirmod tempor invidun

    """
```

---

## Preserve Return Description with `>>` Marker

Use `>>` on its own line inside an existing docstring to provide a description for the return value. On the next `gendocs_new` run the marker is consumed and wired into the `Returns` section automatically.

```python
def square(x: int) -> int:
    """Square a number.

    >> The squared value of x.
    """
    return x * x
```

After running `gendocs_new` (Google style):

```python
def square(x: int) -> int:
    """Square a number.

    Args:
        x (int):
    Returns:
        int: The squared value of x.
    """
    return x * x
```

Combine `$N` for parameter descriptions and `>>` for the return description to fully annotate a function before running the generator — no manual editing of the structured sections needed.

---

## Automatic `Raises` Extraction

`docstring_generator` statically analyzes your function body for `raise` statements and adds a `Raises` section describing each exception — including the condition that triggers it. This works seamlessly with frameworks like **Pydantic**, **FastAPI**, or any custom validation logic.

### Before

```python
class PluginConfig(BaseModel):
    name: str = Field(default="default")
    api_config: dict = Field(default_factory=dict)

    @field_validator("api_config", mode='before')
    @classmethod
    def validate_api_config(cls, values: dict) -> dict:
        required_key_obj = values.get("required_keys", None)
        if not required_key_obj:
            raise ValueError("The first key must be 'required_keys'")
        if not isinstance(required_key_obj, dict):
            raise ValueError("The 'required_keys' must be a dict")
        return values
```

### After running `gendocs_new`

```python
class PluginConfig(BaseModel):
    name: str = Field(default="default")
    api_config: dict = Field(default_factory=dict)

    @field_validator("api_config", mode='before')
    @classmethod
    def validate_api_config(cls, values: dict) -> dict:
        """
        Parameters
        ----------
        values : dict [Argument]

        Returns
        -------
        dict

        Raises
        -------
        ValueError
            If not isinstance(required_key_obj, dict)
        ValueError
            If not required_key_obj
        """
        required_key_obj = values.get("required_keys", None)
        if not required_key_obj:
            raise ValueError("The first key must be 'required_keys'")
        if not isinstance(required_key_obj, dict):
            raise ValueError("The 'required_keys' must be a dict")
        return values
```

Every `raise` — even multiple ones in the same function — is captured, so complex validators document all their failure modes at once.

No more hunting through code to find out what a function can throw — it's documented right where it matters.

---

## Pre-commit Integration

Automatically generate docstrings on every commit using the [pre-commit](https://pre-commit.com/) framework.

### Setup

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

### How it works

The hook runs `gendocs_new` before each commit. If it generates or updates any docstrings, the commit is intentionally stopped so you can review and stage the changes:

| Run | What happens | Status |
|-----|-------------|--------|
| 1st commit | Hook generates docstrings → files modified | ❌ Stopped (intentional) |
| `git add` modified files | Stage the generated docstrings | — |
| 2nd commit | Hook runs, nothing changed | ✅ Passed |

This is standard behavior for any auto-fix hook (same as Black or isort).

### Customizing the style

```yaml
hooks:
  - id: gendocs
    args: [src/, --style, google]
```

---

## IDE Integration

### VS Code Extension

Install the [docstring-generator VS Code extension](https://marketplace.visualstudio.com/items?itemName=felixthec.docstring-generator-vscode) from the marketplace to generate docstrings directly from the editor — no terminal required.

**Features:**
- Right-click any `.py` file → **Generate Docstrings**
- Keyboard shortcut: `Ctrl+Shift+D` (Windows/Linux) / `Cmd+Shift+D` (macOS)
- Configurable style (`numpy`, `google`, `rest`) via VS Code settings

**Setup:**
1. Install from the [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=felixthec.docstring-generator-vscode)
2. Make sure `gendocs_new` is on your `PATH` (install `docstring-generator` via pip)
3. Optionally configure the style in your VS Code settings:
   ```json
   {
     "docstringGenerator.style": "google"
   }
   ```

### JetBrains IDEs (PyCharm, IntelliJ + Python plugin)

Use the provided **File Watcher** configuration to automatically generate docstrings every time you save a `.py` file.

**Setup:**
1. Copy [`gendocs_file_watchers.xml`](gendocs_file_watchers.xml) from the repository root into your project's `.idea/watcherTasks.xml` — or import it via **Settings → Tools → File Watchers → Import**.
2. The watcher is pre-configured to:
   - Run on every `.py` file in the project scope
   - Use `$PROJECT_DIR$/.venv/bin/gendocs_new` as the executable (adjust the path if your venv lives elsewhere)
   - Pass `--style numpy $FilePath$` by default — change `numpy` to `google` or `rest` as needed
   - Write the result back to the same file (`$FilePath$`)

```xml
<TaskOptions>
  <TaskOptions>
    <option name="arguments" value="--style numpy $FilePath$" />
    <option name="fileExtension" value="py" />
    <option name="name" value="gendocs_new" />
    <option name="output" value="$FilePath$" />
    <option name="program" value="$PROJECT_DIR$/.venv/bin/gendocs_new" />
    <option name="scopeName" value="Project Files" />
    <option name="workingDir" value="$FileDir$" />
  </TaskOptions>
</TaskOptions>
```

> **Tip:** Combine the File Watcher with `--ignore-magic` or `pyproject.toml` configuration to tailor which methods are documented automatically on save.

---

## FAQ

### What happens if I re-run docstring generation?

Nothing is lost. If the function signature hasn't changed, the existing docstring stays untouched. If you add or rename parameters, only the structural part is updated — your custom descriptions are preserved.

### Is it safe to use on an existing codebase?

Yes. The tool is non-destructive by design. It never deletes content; it only adds or updates parameter sections based on type hints.

### Does it work with class methods?

Yes — both standalone functions and class methods are fully supported.

---

## Examples

Ready-to-run examples are available in the [`examples/`](examples/) directory.

---

## Installation

```shell
pip install docstring-generator
```

Requires Python 3.13+.

---

## How It Works

The core engine is implemented in C++ (C++20) and exposed to Python via [pybind11](https://github.com/pybind/pybind11), delivering performance that scales to large codebases without slowing down your workflow.

- **Extension:** [docstring-generator-ext](https://github.com/FelixTheC/docstring_generator_ext) — the high-performance backbone of this project

---

## Roadmap

Planned features and areas of investment:

### Medium-term

- [x] File Watcher configuration for JetBrains IDEs (PyCharm) — import `gendocs_file_watchers.xml` to auto-generate docstrings on every file save
- [x] VS Code extension — available on the [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=felixthec.docstring-generator-vscode)
- [ ] GitHub Action — publish a ready-to-use Action to the Marketplace so teams can enforce docstring coverage in CI without any local installation
- [ ] Coverage badge generation (`--badge`) — produce an SVG badge from `--check` results to embed in README, similar to a test-coverage badge
- [ ] JUnit/SARIF output for `--check` — emit machine-readable results for GitHub, GitLab, and Azure DevOps CI panels; enables PR annotations that highlight undocumented functions inline

### Longer-term

- [ ] Watch mode (`--watch`) — monitor the project for file saves and regenerate docstrings automatically in the background
- [ ] Sphinx / mkdocs bridge (`--export-rst`) — generate `.rst` or `.md` stubs ready for Sphinx/mkdocs autodoc pipelines
- [ ] Custom docstring templates — let teams define their own format via `pyproject.toml` for internal style guides that extend NumPy or Google
- [ ] LLM-assisted description generation (opt-in enrichment mode) — use a local or remote LLM to fill in meaningful parameter descriptions beyond the type hint
- [ ] CI/CD pipeline gate (fail build below coverage threshold)

Community feedback shapes priorities — open an issue to vote on features or suggest new ones.

---

## Versioning

Follows [Semantic Versioning](https://semver.org/). See the [tags](../../tags) for all available releases.

## Authors

- **Felix Eisenmenger** — creator & maintainer

## License

MIT License — free to use in personal and commercial projects.