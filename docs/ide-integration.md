# IDE Integration

## VS Code Extension

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

---

## JetBrains IDEs

Use the provided **File Watcher** configuration to automatically generate docstrings every time you save a `.py` file.

**Setup:**

1. Copy [`gendocs_file_watchers.xml`](https://github.com/FelixTheC/docstring_generator/blob/main/gendocs_file_watchers.xml) from the repository root into your project's `.idea/watcherTasks.xml` — or import it via **Settings → Tools → File Watchers → Import**.
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

## Building Your Own Plugin

For a detailed guide on wrapping the CLI inside a VS Code extension or JetBrains plugin — including code samples in TypeScript and Kotlin — see the [plugin guide](plugin-guide.md).
