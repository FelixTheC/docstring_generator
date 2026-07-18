# Docstring Generator

An automated docstring generator for Python developers. This extension integrates your local environment's `docstring-generator` CLI tool directly into VS Code to effortlessly generate docstrings from your type hints.

## Features

* 🚀 **Automated Generation:** Analyzes your Python functions and class methods to generate docstrings instantly.
* 📦 **Multiple Formats:** Out-of-the-box support for **NumPy**, **Google**, and **reStructuredText** documentation styles.
* 🐍 **Environment Aware:** Seamlessly detects and operates inside your workspace's active virtual environment (venv, conda, etc.).

## Requirements

To use this extension, you need:
1. The official **[Python extension for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-python.python)** installed (used to detect your active virtual environment).
2. The `docstring-generator` library installed in your target Python environment:
```bash
pip install docstring-generator
```

## Usage

1. Open any Python file (`.py`).
2. Press `Ctrl+Shift+D` (or `Cmd+Shift+D` on macOS) to instantly generate docstrings for the functions and class methods in the current file.

## Extension Settings

This extension contributes the following configuration settings under `docstringGenerator`:

* `docstringGenerator.style`: Specifies the style of docstring to generate. Options: `numpy` (default), `google`, or `rest`.

## Release Notes

### 1.0.0

* Initial release of the Docstring Generator extension.
* Automated file parsing and formatting support via `docstring-generator` CLI.
* Context-aware Python environment resolution.


## Extension Settings

Include if your extension adds any VS Code settings through the `contributes.configuration` extension point.

For example:

This extension contributes the following settings:

* `docstringGenerator.enable`: Enable/disable this extension.
* `docstringGenerator.style`: Set to the style of docstring to generate. [`numpy`, `google`, `rest`]
* `docstringGenerator.ignoremagic`: Ignore magic commands in docstring generation. (default: `true`)


## Release Notes

Users appreciate release notes as you update your extension.

### 1.0.0
- Initial release of the Docstring Generator extension.
- Automated file parsing and formatting support via docstring-generator CLI.
- Context-aware Python environment resolution.

### 1.0.1
- Added support for ignoring magic commands in docstring generation. (The flag was missing from the configuration settings.)

### 💡 Key Improvements Made:
* **Prerequisites Clarified:** Explicitly listed the **Microsoft Python Extension** as a prerequisite. This saves you from getting GitHub issues or 1-star reviews from users wondering why it isn't picking up their specific virtual environment paths.
* **Removed Boilerplate:** Swapped out the generic placeholder text ("*Include if your extension adds...*") with clean, professional explanations.
* **Formatting Cleanup:** Cleaned up the shortcut instructions and config variable listing to reflect the exact `style` setting you implemented in your code.

## Usage

* Press `Ctrl+Shift+d` (Windows, Linux, macOS) to let the `docstring-generator` generate docstrings for functions and class methods from their type hints of the current file.

