# docstring_generator

[![Python 3.10](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/docstring-generator.svg)](https://badge.fury.io/py/docstring-generator)
![Actions](https://github.com/FelixTheC/docstring_generator/actions/workflows/python-app.yml/badge.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![](https://img.shields.io/pypi/dm/docstring-generator.svg)](https://pypi.org/project/docstring-generator/)
[![VS Code Extension](https://img.shields.io/badge/VS%20Code-Extension-007ACC?logo=visualstudiocode&logoColor=white)](https://marketplace.visualstudio.com/items?itemName=felixthec.docstring-generator-vscode)

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
- 🚨 **Exception-aware** — automatically detects `raise` statements and documents them in a `Raises` section
- 🙈 **Convention-correct** — `self` and `cls` are automatically excluded from generated parameter sections
- ⚙️ **Async-ready** — handles both `def` and `async def` functions transparently
- 🎨 **Style-safe** — detects the existing docstring style and refuses to silently mix conventions
- 🏎️ **Blazing fast** — core engine written in C++ via [pybind11](https://github.com/FelixTheC/docstring_generator_ext)

---

## Quick Start

```shell
pip install docstring-generator
```

```shell
gendocs_new file.py        # single file
gendocs_new mydir/         # entire directory
```

That's it. Your functions now have properly formatted docstrings.

> 💡 **Prefer working inside your editor?** Install the [VS Code extension](https://marketplace.visualstudio.com/items?itemName=felixthec.docstring-generator-vscode) or use the [JetBrains File Watcher](ide-integration.md#jetbrains-ides) to generate docstrings automatically on every save.

---

## How It Works

The core engine is implemented in C++ (C++20) and exposed to Python via [pybind11](https://github.com/pybind/pybind11), delivering performance that scales to large codebases without slowing down your workflow.

- **Extension:** [docstring-generator-ext](https://github.com/FelixTheC/docstring_generator_ext) — the high-performance backbone of this project

---

## License

Apache-2.0 — free to use in personal and commercial projects.

---

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/FEisenmenger)
