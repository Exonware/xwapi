# XWJSON Visual Studio Extension - Quick Reference

## Summary

To create a Visual Studio extension for viewing XWJSON files, you have two main options:

### Option 1: Visual Studio Extension (C#)
- **Best for:** Full Visual Studio integration
- **Language:** C#
- **Complexity:** Medium-High
- **See:** `VISUAL_STUDIO_EXTENSION_GUIDE.md`

### Option 2: VS Code Extension (TypeScript)
- **Best for:** Easier development, cross-platform
- **Language:** TypeScript/JavaScript
- **Complexity:** Low-Medium
- **See:** `VSCODE_EXTENSION_GUIDE.md`

## Key Components Needed

### 1. File Icon
- Create custom `.ico` (VS) or `.svg` (VS Code) icon
- Register file association for `.xwjson` extension
- Display in Solution Explorer / File Explorer

### 2. File Viewer/Editor
- Custom editor provider that:
  - Detects `.xwjson` files
  - Calls Python to decode binary format
  - Displays decoded JSON with syntax highlighting
  - Optionally shows metadata/header info

### 3. Python Integration
- Required: Python installed with `exonware-xwjson` package
- Decode script:
  ```python
  from exonware.xwjson import XWJSONSerializer
  import json
  
  serializer = XWJSONSerializer()
  data = serializer.load_file("file.xwjson")
  print(json.dumps(data, indent=2))
  ```

## XWJSON File Format Details

- **Extension:** `.xwjson`
- **Format:** Binary (MessagePack-based)
- **Magic Bytes:** `b'XWJ1'` (Extended JSON v1)
- **Structure:** Header + Data + Metadata + Index
- **Decoding:** Must use Python library (no native C# decoder available)

## Quick Start (VS Code Extension - Easiest)

1. **Install prerequisites:**
   ```bash
   npm install -g yo generator-code
   ```

2. **Create extension:**
   ```bash
   yo code
   # Select: New Extension (TypeScript)
   ```

3. **Add Python helper** (see `VSCODE_EXTENSION_GUIDE.md`)

4. **Register custom editor** in `package.json`

5. **Test:** Press F5 to launch Extension Development Host

## Quick Start (Visual Studio Extension)

1. **Install Visual Studio SDK**

2. **Create VSIX Project:**
   - File → New → Project → Extensibility → VSIX Project

3. **Add components:**
   - Icon provider class
   - Editor factory class
   - WPF viewer control
   - Python helper class

4. **Register in manifest:**
   - File associations
   - Editor factory
   - Icon provider

5. **Test:** Press F5 to launch Experimental Instance

## Python Requirements

Users must have:
```bash
pip install exonware-xwjson
```

Or with full dependencies:
```bash
pip install exonware-xwjson[full]
```

## Icon Suggestions

- Use distinct color (purple/blue) to differentiate from JSON
- Include "XW" text or binary indicator
- Sizes: 16x16, 32x32, 48x48, 256x256 (for .ico)

## Alternative: Standalone Viewer

If extension development is too complex, consider:
1. **Standalone WPF/WinForms app** that opens `.xwjson` files
2. **Windows file association** to open with your app
3. **Context menu** "Open with XWJSON Viewer"

This provides file viewing without VS integration.

## Testing Checklist

- [ ] Custom icon appears in file explorer
- [ ] Double-clicking `.xwjson` opens in custom viewer
- [ ] JSON content displays correctly
- [ ] Syntax highlighting works
- [ ] Error handling for missing Python/library
- [ ] Large files handled gracefully
- [ ] Performance is acceptable

## Common Issues

**Issue:** Python not found
- **Solution:** Check PATH, provide Python path in settings

**Issue:** `exonware-xwjson` not installed
- **Solution:** Guide user to install: `pip install exonware-xwjson`

**Issue:** Binary file appears as text
- **Solution:** Ensure custom editor is registered and has higher priority

**Issue:** Slow loading for large files
- **Solution:** Add loading indicator, consider caching, lazy loading

## Next Steps

1. Choose your approach (VS Extension vs VS Code Extension)
2. Follow the detailed guide for your chosen option
3. Create icon assets
4. Implement Python integration
5. Test with sample `.xwjson` files
6. Package and distribute

## Resources

- **XWJSON Library:** `xwjson/README.md`
- **VS Extension Guide:** `VISUAL_STUDIO_EXTENSION_GUIDE.md`
- **VS Code Extension Guide:** `VSCODE_EXTENSION_GUIDE.md`
- **Visual Studio SDK:** https://docs.microsoft.com/en-us/visualstudio/extensibility/
- **VS Code Extension API:** https://code.visualstudio.com/api
