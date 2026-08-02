# Building Your Own Plugin

The core strategy is simple: **wrap the CLI, don't rewrite logic**. Both IDEs support running external tools/processes, so you call `gendocs_new` from the plugin. This means:

- One codebase to maintain (the CLI)
- Plugins stay thin: UI glue + process invocation
- Users who already have the package installed get the IDE features automatically

---

## VS Code Extension

VS Code extensions are written in **TypeScript/JavaScript**.

### Minimal structure

```
docstring-generator-vscode/
├── package.json          ← manifest + activation events
├── src/
│   └── extension.ts      ← entry point
└── tsconfig.json
```

### Command: Generate docstrings for current file

```typescript
import * as vscode from 'vscode';
import { execSync } from 'child_process';

export function activate(context: vscode.ExtensionContext) {
    const cmd = vscode.commands.registerCommand('docstring-generator.generateFile', () => {
        const file = vscode.window.activeTextEditor?.document.fileName;
        if (!file?.endsWith('.py')) return;

        const style = vscode.workspace.getConfiguration('docstringGenerator').get('style', 'numpy');
        try {
            execSync(`gendocs_new --style ${style} "${file}"`);
            vscode.commands.executeCommand('workbench.action.files.revert');
        } catch (e) {
            vscode.window.showErrorMessage(`docstring_generator failed: ${e}`);
        }
    });

    context.subscriptions.push(cmd);
}
```

### `package.json` highlights

```json
{
  "activationEvents": ["onLanguage:python"],
  "contributes": {
    "commands": [{
      "command": "docstring-generator.generateFile",
      "title": "Generate Docstrings"
    }],
    "configuration": {
      "properties": {
        "docstringGenerator.style": {
          "type": "string",
          "enum": ["numpy", "google", "rest"],
          "default": "numpy"
        }
      }
    },
    "keybindings": [{
      "command": "docstring-generator.generateFile",
      "key": "ctrl+shift+d",
      "when": "editorLangId == python"
    }]
  }
}
```

**Resources:**

- [VS Code Extension API](https://code.visualstudio.com/api)
- [Your First Extension](https://code.visualstudio.com/api/get-started/your-first-extension)
- Publish to [VS Code Marketplace](https://marketplace.visualstudio.com/manage)

---

## JetBrains Plugin (PyCharm / IntelliJ)

JetBrains plugins are written in **Kotlin** (or Java).

### Minimal structure

```
docstring-generator-intellij/
├── build.gradle.kts
├── src/main/
│   ├── kotlin/
│   │   └── GenerateDocstringsAction.kt
│   └── resources/
│       └── META-INF/plugin.xml
```

### `AnAction` that calls the CLI

```kotlin
import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.vfs.VirtualFileManager

class GenerateDocstringsAction : AnAction() {
    override fun actionPerformed(e: AnActionEvent) {
        val file = e.getData(CommonDataKeys.VIRTUAL_FILE) ?: return
        if (file.extension != "py") return

        val process = ProcessBuilder("gendocs_new", file.path)
            .redirectErrorStream(true)
            .start()
        process.waitFor()

        VirtualFileManager.getInstance().refreshWithoutFileWatcher(false)
    }

    override fun update(e: AnActionEvent) {
        e.presentation.isEnabledAndVisible =
            e.getData(CommonDataKeys.VIRTUAL_FILE)?.extension == "py"
    }
}
```

### `plugin.xml` registration

```xml
<actions>
  <action id="GenerateDocstrings"
          class="GenerateDocstringsAction"
          text="Generate Docstrings"
          description="Run docstring_generator on this file">
    <add-to-group group-id="EditorPopupMenu" anchor="last"/>
    <keyboard-shortcut keymap="$default" first-keystroke="ctrl shift D"/>
  </action>
</actions>
```

**Resources:**

- [IntelliJ Platform SDK](https://plugins.jetbrains.com/docs/intellij/welcome.html)
- [Plugin Gradle Template](https://github.com/JetBrains/intellij-platform-plugin-template)
- Publish to [JetBrains Marketplace](https://plugins.jetbrains.com/author/me)

---

## Recommended Build Order

| Step | What | Why |
|------|------|-----|
| 1 | VS Code extension | Simpler API, TypeScript, faster iteration |
| 2 | Keyboard shortcut + right-click menu | The two most-used entry points |
| 3 | Settings UI for `--style` | Makes it feel polished |
| 4 | JetBrains plugin | Larger Python dev audience in enterprise |
| 5 | Auto-run on save (optional) | Power-user feature, add last |

> **Gotcha:** Make sure `gendocs_new` is on `PATH` in the IDE's process environment. On macOS especially, GUI apps don't inherit the shell PATH. The robust fix is to let users configure the executable path in the plugin settings.
