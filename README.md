[![Python 3.10](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/docstring-generator.svg)](https://badge.fury.io/py/docstring-generator)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![](https://img.shields.io/pypi/dm/docstring-generator.svg)](https://pypi.org/project/docstring-generator/)

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

---

## Options

### `--style` — Choose your docstring convention

| Style | Flag | Description |
|-------|------|-------------|
| NumPy | `--style numpy` | Standard in scientific Python (default) |
| Google | `--style google` | Preferred in many enterprise codebases |
| reStructuredText | `--style rest` | Compatible with Sphinx auto-documentation |

**Default:** `numpy`

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
        cls : [Argument]
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

Requires Python 3.10+.

---

## How It Works

The core engine is implemented in C++ and exposed to Python via [pybind11](https://github.com/pybind/pybind11), delivering performance that scales to large codebases without slowing down your workflow.

- **Extension:** [docstring-generator-ext](https://github.com/FelixTheC/docstring_generator_ext) — the high-performance backbone of this project

---

## Roadmap

Planned features and areas of investment:

- [x] Pre-commit hook integration for automatic docstring enforcement
- [x] Return type documentation generation
- [x] Raises documentation generation
- [ ] CI/CD pipeline integration & docstring coverage reporting
- [ ] IDE plugin support (JetBrains, VS Code)
- [ ] LLM-assisted description generation (opt-in enrichment mode)

Community feedback shapes priorities — open an issue to vote on features or suggest new ones.

---

## Versioning

Follows [Semantic Versioning](https://semver.org/). See the [tags](../../tags) for all available releases.

## Authors

- **Felix Eisenmenger** — creator & maintainer

## License

MIT License — free to use in personal and commercial projects.