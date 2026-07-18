// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import {execSync} from "node:child_process";

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export async function activate(context: vscode.ExtensionContext) {

    const pythonExtension = vscode.extensions.getExtension('ms-python.python');

    if (!pythonExtension) {
        vscode.window.showErrorMessage("The official Python extension is required.");
        return;
    }

    if (!pythonExtension.isActive) {
        await pythonExtension.activate();
    }

    const pythonApi = pythonExtension.exports;

    const cmd = vscode.commands.registerCommand('docstring-generator.generateFile', async () => {
        const file = vscode.window.activeTextEditor?.document.fileName;
        if (!file?.endsWith('.py')) {
            return;
        }

        const style = vscode.workspace.getConfiguration('docstringGenerator').get('style', 'numpy');
        const activeWorkspaceFolder = vscode.workspace.workspaceFolders?.[0];

        try {
const environment = await pythonApi.environments.resolveEnvironment(
                pythonApi.environments.getActiveEnvironmentPath(activeWorkspaceFolder?.uri)
            );
            const pythonExecutablePath = environment?.executable.uri?.fsPath;

            let toolCmd = 'gendocs_new';

            if (pythonExecutablePath) {
                const path = require('path');
                const fs = require('fs');

                // Get the bin directory containing the python executable
                const binDir = path.dirname(pythonExecutablePath);
                const isWindows = process.platform === 'win32';
                const binaryName = isWindows ? 'gendocs_new.exe' : 'gendocs_new';
                const fullToolPath = path.join(binDir, binaryName);

                // If the binary exists inside your active venv, use its absolute path!
                if (fs.existsSync(fullToolPath)) {
                    toolCmd = fullToolPath;
                }
            }

            execSync(`"${toolCmd}" --style ${style} "${file}"`);

            // Reload the file so the editor shows the new docstrings
            await vscode.commands.executeCommand('workbench.action.files.revert');
            vscode.window.showInformationMessage("Documentation generated!");
        } catch (e) {
            vscode.window.showErrorMessage(`docstring_generator failed: ${e}`);
        }
    });

    context.subscriptions.push(cmd);
}

// This method is called when your extension is deactivated
export function deactivate() {
    // as this is only a CLI tool, we don't need to do anything here
}
