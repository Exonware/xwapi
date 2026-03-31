# VS Code Extension for XWJSON Viewer

## Overview

This guide explains how to create a VS Code extension (TypeScript/JavaScript) that provides:
- Custom icon for `.xwjson` files
- Custom text editor provider to view decoded XWJSON content
- Syntax highlighting for the JSON output

## Why VS Code Extension?

- **Easier to develop** - TypeScript/JavaScript is simpler than C# VS extensions
- **Cross-platform** - Works on Windows, Mac, Linux
- **Large community** - Many examples and resources
- **Modern VS** - Visual Studio 2022+ can use VS Code extensions in some scenarios

## Prerequisites

- Node.js (v14+)
- npm or yarn
- TypeScript
- VS Code Extension Generator: `npm install -g yo code-generator`

## Project Setup

### Step 1: Create Extension Project

```bash
npm install -g yo generator-code
yo code
```

Select:
- **New Extension (TypeScript)**
- Name: `xwjson-viewer`
- Identifier: `exonware.xwjson-viewer`
- Description: "Viewer for XWJSON binary format"
- Initialize git: Yes

### Step 2: Project Structure

```
xwjson-viewer/
├── package.json
├── tsconfig.json
├── src/
│   ├── extension.ts          # Main extension entry
│   ├── xwjsonProvider.ts     # Custom document provider
│   └── pythonHelper.ts       # Python integration
├── resources/
│   └── xwjson-icon.svg       # Custom icon
└── README.md
```

## Implementation

### Step 1: Update package.json

```json
{
  "name": "xwjson-viewer",
  "displayName": "XWJSON Viewer",
  "description": "Viewer for XWJSON binary format files",
  "version": "0.0.1",
  "engines": {
    "vscode": "^1.74.0"
  },
  "categories": ["Other"],
  "activationEvents": [
    "onCustomEditor:xwjson.viewer"
  ],
  "main": "./out/extension.js",
  "contributes": {
    "customEditors": [
      {
        "viewType": "xwjson.viewer",
        "displayName": "XWJSON Viewer",
        "selector": [
          {
            "filenamePattern": "*.xwjson"
          }
        ],
        "priority": "default"
      }
    ],
    "fileAssociations": [
      {
        "pattern": "*.xwjson",
        "icon": "resources/xwjson-icon.svg"
      }
    ],
    "languages": [
      {
        "id": "xwjson-json",
        "aliases": ["XWJSON", "xwjson"],
        "extensions": [".xwjson"]
      }
    ],
    "grammars": [
      {
        "language": "xwjson-json",
        "scopeName": "source.json",
        "path": "./syntaxes/json.tmLanguage.json"
      }
    ]
  },
  "scripts": {
    "vscode:prepublish": "npm run compile",
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./"
  },
  "devDependencies": {
    "@types/vscode": "^1.74.0",
    "@types/node": "16.x",
    "typescript": "^4.9.4"
  }
}
```

### Step 2: Python Helper (pythonHelper.ts)

```typescript
import * as vscode from 'vscode';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as path from 'path';

const execAsync = promisify(exec);

export class PythonHelper {
    private pythonPath: string | null = null;

    async findPython(): Promise<string> {
        if (this.pythonPath) {
            return this.pythonPath;
        }

        // Try to find Python
        const pythonCommands = ['python3', 'python', 'py'];
        
        for (const cmd of pythonCommands) {
            try {
                const { stdout } = await execAsync(`${cmd} --version`);
                if (stdout.includes('Python')) {
                    this.pythonPath = cmd;
                    return cmd;
                }
            } catch (error) {
                // Continue to next command
            }
        }

        throw new Error('Python not found. Please install Python and ensure it is in your PATH.');
    }

    async decodeXWJSONToJSON(xwjsonPath: string): Promise<string> {
        const python = await this.findPython();
        
        const script = `
import sys
import json
from pathlib import Path
try:
    from exonware.xwjson import XWJSONSerializer
    serializer = XWJSONSerializer()
    data = serializer.load_file(sys.argv[1])
    print(json.dumps(data, indent=2, ensure_ascii=False))
except ImportError as e:
    print(f'ERROR: Missing dependency: {e}', file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
        `.trim();

        // Create temporary script file
        const tempDir = path.join(__dirname, '..', 'temp');
        const fs = require('fs');
        if (!fs.existsSync(tempDir)) {
            fs.mkdirSync(tempDir, { recursive: true });
        }
        const tempScript = path.join(tempDir, 'decode_xwjson.py');
        fs.writeFileSync(tempScript, script);

        try {
            const { stdout, stderr } = await execAsync(
                `"${python}" "${tempScript}" "${xwjsonPath}"`,
                { maxBuffer: 10 * 1024 * 1024 } // 10MB buffer
            );

            if (stderr && stderr.includes('ERROR')) {
                throw new Error(stderr);
            }

            return stdout;
        } catch (error: any) {
            throw new Error(`Failed to decode XWJSON: ${error.message}`);
        } finally {
            // Clean up temp script
            if (fs.existsSync(tempScript)) {
                fs.unlinkSync(tempScript);
            }
        }
    }
}
```

### Step 3: Custom Editor Provider (xwjsonProvider.ts)

```typescript
import * as vscode from 'vscode';
import { PythonHelper } from './pythonHelper';

export class XWJSONEditorProvider implements vscode.CustomTextEditorProvider {
    private pythonHelper: PythonHelper;

    constructor(private readonly context: vscode.ExtensionContext) {
        this.pythonHelper = new PythonHelper();
    }

    public static register(context: vscode.ExtensionContext): vscode.Disposable {
        const provider = new XWJSONEditorProvider(context);
        const providerRegistration = vscode.window.registerCustomEditorProvider(
            'xwjson.viewer',
            provider,
            {
                webviewOptions: {
                    retainContextWhenHidden: true,
                },
                supportsMultipleEditorsPerDocument: false,
            }
        );
        return providerRegistration;
    }

    public async resolveCustomTextEditor(
        document: vscode.TextDocument,
        webviewPanel: vscode.WebviewPanel,
        _token: vscode.CancellationToken
    ): Promise<void> {
        // For binary files, we'll use a text editor with decoded content
        // Create a virtual document with decoded JSON
        await this.updateView(document, webviewPanel);
    }

    private async updateView(
        document: vscode.TextDocument,
        webviewPanel: vscode.WebviewPanel
    ): Promise<void> {
        try {
            webviewPanel.webview.html = this.getHtmlForWebview('Loading...');

            const jsonContent = await this.pythonHelper.decodeXWJSONToJSON(
                document.uri.fsPath
            );

            // Update the document with decoded JSON (read-only)
            const edit = new vscode.WorkspaceEdit();
            const fullRange = new vscode.Range(
                document.positionAt(0),
                document.positionAt(document.getText().length)
            );
            edit.replace(document.uri, fullRange, jsonContent);
            await vscode.workspace.applyEdit(edit);

            // Set language mode to JSON for syntax highlighting
            await vscode.languages.setTextDocumentLanguage(document, 'json');

            webviewPanel.webview.html = this.getHtmlForWebview(
                'XWJSON decoded successfully. View in editor.'
            );
        } catch (error: any) {
            webviewPanel.webview.html = this.getHtmlForWebview(
                `Error: ${error.message}`
            );
        }
    }

    private getHtmlForWebview(content: string): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XWJSON Viewer</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            padding: 20px;
            color: var(--vscode-foreground);
        }
        .status {
            padding: 10px;
            border-radius: 4px;
            background: var(--vscode-input-background);
        }
        .error {
            color: var(--vscode-errorForeground);
        }
    </style>
</head>
<body>
    <div class="status ${content.includes('Error') ? 'error' : ''}">
        ${content}
    </div>
    <p>The decoded JSON content is displayed in the editor with JSON syntax highlighting.</p>
</body>
</html>`;
    }
}
```

### Step 4: Extension Entry Point (extension.ts)

```typescript
import * as vscode from 'vscode';
import { XWJSONEditorProvider } from './xwjsonProvider';

export function activate(context: vscode.ExtensionContext) {
    console.log('XWJSON Viewer extension is now active!');

    // Register custom editor provider
    const providerRegistration = XWJSONEditorProvider.register(context);
    context.subscriptions.push(providerRegistration);

    // Register command to refresh view
    const refreshCommand = vscode.commands.registerCommand(
        'xwjson.viewer.refresh',
        async () => {
            const activeEditor = vscode.window.activeTextEditor;
            if (activeEditor && activeEditor.document.fileName.endsWith('.xwjson')) {
                // Trigger refresh
                vscode.commands.executeCommand('workbench.action.reloadWindow');
            }
        }
    );
    context.subscriptions.push(refreshCommand);
}

export function deactivate() {}
```

## Icon Design

Create `resources/xwjson-icon.svg`:

```svg
<svg width="16" height="16" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
  <rect width="16" height="16" fill="#6B46C1" rx="2"/>
  <text x="8" y="12" font-family="monospace" font-size="10" fill="white" text-anchor="middle" font-weight="bold">XW</text>
</svg>
```

## Building and Testing

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Compile TypeScript:**
   ```bash
   npm run compile
   ```

3. **Run extension:**
   - Press `F5` in VS Code
   - This opens a new Extension Development Host window
   - Open a `.xwjson` file in that window

4. **Package for distribution:**
   ```bash
   npm install -g vsce
   vsce package
   ```

## Installation Requirements

Users need:
1. Python installed and in PATH
2. `exonware-xwjson` package installed: `pip install exonware-xwjson`

## Alternative: Simpler Text Document Provider

Instead of a custom editor, you can create a simpler text document provider that automatically decodes XWJSON when opened:

```typescript
// Simpler approach - just decode and show as JSON
export class XWJSONTextDocumentContentProvider implements vscode.TextDocumentContentProvider {
    private pythonHelper: PythonHelper = new PythonHelper();

    async provideTextDocumentContent(uri: vscode.Uri): Promise<string> {
        try {
            return await this.pythonHelper.decodeXWJSONToJSON(uri.fsPath);
        } catch (error: any) {
            return `// Error loading XWJSON file: ${error.message}`;
        }
    }
}
```

## Resources

- [VS Code Extension API](https://code.visualstudio.com/api)
- [Custom Editors Guide](https://code.visualstudio.com/api/extension-guides/custom-editors)
- [VS Code Extension Samples](https://github.com/Microsoft/vscode-extension-samples)
