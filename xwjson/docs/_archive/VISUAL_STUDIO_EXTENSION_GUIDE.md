# Visual Studio Extension for XWJSON Viewer

## Overview

This guide explains how to create a Visual Studio extension that allows you to:
- View `.xwjson` files with syntax highlighting
- Display a custom icon for `.xwjson` files in Solution Explorer
- Provide a custom editor/viewer for XWJSON binary format

## Technology Options

### Option 1: Visual Studio Extension (C#) - Recommended for Visual Studio

**Language:** C#  
**Framework:** .NET Framework or .NET (depending on VS version)  
**SDK:** Visual Studio SDK

**Pros:**
- Native integration with Visual Studio
- Full access to VS APIs
- Better performance
- Can integrate with Solution Explorer, Properties window, etc.

**Cons:**
- More complex setup
- Requires Visual Studio SDK
- Windows-only (typically)

### Option 2: Visual Studio Code Extension (TypeScript/JavaScript) - Alternative

**Language:** TypeScript/JavaScript  
**Framework:** VS Code Extension API

**Pros:**
- Cross-platform (Windows, Mac, Linux)
- Easier to develop
- Large community and examples
- Can work with VS Code and potentially VS 2022+ (if using VS Code-based editor)

**Cons:**
- May not have full VS integration
- Different API than traditional VS extensions

## Recommended Approach: Visual Studio Extension (C#)

Since you're using Visual Studio, we'll focus on creating a C# extension.

## Architecture

The extension will consist of:

1. **File Icon Provider** - Custom icon for `.xwjson` files
2. **Editor Factory** - Custom editor/viewer for XWJSON files
3. **Language Service** - Optional syntax highlighting (if converting to JSON view)
4. **Python Integration** - Call Python library to decode XWJSON to JSON for viewing

## Implementation Steps

### Step 1: Project Setup

1. **Install Prerequisites:**
   - Visual Studio 2022 (or your version)
   - Visual Studio SDK
   - .NET Framework SDK (or .NET SDK depending on VS version)

2. **Create Extension Project:**
   ```
   File → New → Project → Extensibility → VSIX Project
   ```

3. **Project Structure:**
   ```
   XWJSONViewerExtension/
   ├── XWJSONViewerExtension.csproj
   ├── source.extension.vsixmanifest
   ├── XWJSONEditorFactory.cs          # Custom editor
   ├── XWJSONIconProvider.cs            # Icon provider
   ├── XWJSONViewerControl.xaml         # WPF viewer control
   ├── XWJSONViewerControl.xaml.cs      # Code-behind
   ├── PythonHelper.cs                  # Python integration
   └── Resources/
       └── xwjson.ico                   # Custom icon
   ```

### Step 2: File Icon Provider

Create a class to provide custom icons for `.xwjson` files:

```csharp
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;
using System;
using System.Runtime.InteropServices;

[Guid("YOUR-GUID-HERE")]
public class XWJSONIconProvider : IVsFileIconProvider
{
    public int GetFileIcon(string pszPath, out int pIndex, out uint pdwFlags)
    {
        pIndex = 0;
        pdwFlags = 0;
        
        if (pszPath.EndsWith(".xwjson", StringComparison.OrdinalIgnoreCase))
        {
            // Return custom icon index
            pIndex = 1; // Index in your icon resource
            return VSConstants.S_OK;
        }
        
        return VSConstants.E_NOTIMPL;
    }
}
```

### Step 3: Editor Factory

Create a custom editor factory to open XWJSON files:

```csharp
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;
using System;
using System.Runtime.InteropServices;

[Guid("YOUR-EDITOR-GUID-HERE")]
public class XWJSONEditorFactory : IVsEditorFactory
{
    private Package package;
    
    public XWJSONEditorFactory(Package package)
    {
        this.package = package;
    }
    
    public int CreateEditorInstance(
        uint grfCreateDoc,
        string pszMkDocument,
        string pszPhysicalView,
        IVsHierarchy pvHier,
        uint itemid,
        IntPtr punkDocDataExisting,
        out IntPtr ppunkDocView,
        out IntPtr ppunkDocData,
        out string pbstrEditorCaption,
        out Guid pguidCmdUI,
        out int pgrfCDW)
    {
        ppunkDocView = IntPtr.Zero;
        ppunkDocData = IntPtr.Zero;
        pbstrEditorCaption = null;
        pguidCmdUI = Guid.Empty;
        pgrfCDW = 0;
        
        // Create your custom editor/viewer
        var viewer = new XWJSONViewerControl();
        ppunkDocView = Marshal.GetIUnknownForObject(viewer);
        
        return VSConstants.S_OK;
    }
    
    // Implement other IVsEditorFactory methods...
}
```

### Step 4: Python Integration

Since XWJSON is a Python library, you'll need to call Python to decode the binary format:

```csharp
using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading.Tasks;

public class PythonHelper
{
    private string pythonPath;
    
    public PythonHelper()
    {
        // Find Python installation
        pythonPath = FindPython();
    }
    
    private string FindPython()
    {
        // Try common Python locations
        var paths = new[]
        {
            @"C:\Python39\python.exe",
            @"C:\Python310\python.exe",
            @"C:\Python311\python.exe",
            @"C:\Program Files\Python39\python.exe",
            Environment.GetEnvironmentVariable("PYTHON_HOME") + @"\python.exe"
        };
        
        foreach (var path in paths)
        {
            if (File.Exists(path))
                return path;
        }
        
        // Try python from PATH
        return "python";
    }
    
    public async Task<string> DecodeXWJSONToJSON(string xwjsonPath)
    {
        var script = @"
import sys
import json
from pathlib import Path
from exonware.xwjson import XWJSONSerializer

try:
    serializer = XWJSONSerializer()
    data = serializer.load_file(sys.argv[1])
    print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
";
        
        var tempScript = Path.GetTempFileName() + ".py";
        File.WriteAllText(tempScript, script);
        
        try
        {
            var process = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = pythonPath,
                    Arguments = $"\"{tempScript}\" \"{xwjsonPath}\"",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                }
            };
            
            process.Start();
            var output = await process.StandardOutput.ReadToEndAsync();
            var error = await process.StandardError.ReadToEndAsync();
            await process.WaitForExitAsync();
            
            if (process.ExitCode != 0)
            {
                throw new Exception($"Python error: {error}");
            }
            
            return output;
        }
        finally
        {
            if (File.Exists(tempScript))
                File.Delete(tempScript);
        }
    }
}
```

### Step 5: Viewer Control (WPF)

Create a WPF control to display the decoded JSON:

```xml
<!-- XWJSONViewerControl.xaml -->
<UserControl x:Class="XWJSONViewerExtension.XWJSONViewerControl"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
        </Grid.RowDefinitions>
        
        <StackPanel Grid.Row="0" Orientation="Horizontal" Margin="5">
            <TextBlock Text="XWJSON Viewer" FontWeight="Bold" Margin="5,0"/>
            <Button Content="Refresh" Click="Refresh_Click" Margin="5,0"/>
        </StackPanel>
        
        <ScrollViewer Grid.Row="1" VerticalScrollBarVisibility="Auto">
            <TextBox x:Name="JsonTextBox" 
                     IsReadOnly="True" 
                     FontFamily="Consolas"
                     FontSize="12"
                     TextWrapping="Wrap"
                     Background="#1E1E1E"
                     Foreground="#D4D4D4"/>
        </ScrollViewer>
    </Grid>
</UserControl>
```

```csharp
// XWJSONViewerControl.xaml.cs
using System;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;

public partial class XWJSONViewerControl : UserControl
{
    private string currentFilePath;
    private PythonHelper pythonHelper;
    
    public XWJSONViewerControl()
    {
        InitializeComponent();
        pythonHelper = new PythonHelper();
    }
    
    public void LoadFile(string filePath)
    {
        currentFilePath = filePath;
        RefreshContent();
    }
    
    private async void Refresh_Click(object sender, RoutedEventArgs e)
    {
        await RefreshContent();
    }
    
    private async Task RefreshContent()
    {
        if (string.IsNullOrEmpty(currentFilePath))
            return;
        
        try
        {
            JsonTextBox.Text = "Loading...";
            var json = await pythonHelper.DecodeXWJSONToJSON(currentFilePath);
            JsonTextBox.Text = json;
        }
        catch (Exception ex)
        {
            JsonTextBox.Text = $"Error loading file: {ex.Message}";
        }
    }
}
```

### Step 6: Register Extension

Update `source.extension.vsixmanifest`:

```xml
<PackageManifest>
  <Metadata>
    <Identity Id="XWJSONViewerExtension" Version="1.0" Language="en-US" Publisher="YourName"/>
    <DisplayName>XWJSON Viewer</DisplayName>
    <Description>Viewer for XWJSON binary format files</Description>
  </Metadata>
  <Assets>
    <Asset Type="Microsoft.VisualStudio.VsPackage" d:Source="File" 
           Path="XWJSONViewerExtension.pkgdef" d:VsixSubPath="XWJSONViewerExtension.pkgdef"/>
  </Assets>
  <Installation>
    <InstallationTarget Id="Microsoft.VisualStudio.Community" Version="[17.0,18.0)"/>
  </Installation>
</PackageManifest>
```

Create `XWJSONViewerExtension.pkgdef`:

```
[$RootKey$\FileIconProviders\{YOUR-GUID-HERE}]
@="XWJSON Icon Provider"
"Path"="XWJSONViewerExtension.dll"

[$RootKey$\Editors\{YOUR-EDITOR-GUID-HERE}]
@="XWJSON Editor"
"DisplayName"="XWJSON Editor"
"ExcludeDefTextEditor"=dword:00000001
"Package"="{YOUR-PACKAGE-GUID-HERE}"
"CommonPhysicalViewAttributes"=dword:00000001

[$RootKey$\Editors\{YOUR-EDITOR-GUID-HERE}\Extensions]
".xwjson"=dword:00000001
```

## Alternative: Simpler Approach with File Association

If you want a simpler solution, you can:

1. **Create a standalone viewer application** (WPF or WinForms)
2. **Register file association** in Windows Registry
3. **Add context menu** "Open with XWJSON Viewer"

This doesn't require a full VS extension but provides file viewing capability.

## Icon Design

Create a custom icon (`xwjson.ico`) that represents XWJSON:
- Use a JSON-like icon with "XW" or binary indicator
- 16x16, 32x32, 48x48, 256x256 sizes
- Consider using a distinct color (e.g., purple/blue) to differentiate from JSON

## Testing

1. Build the extension in Debug mode
2. Press F5 to launch Experimental Instance of Visual Studio
3. Open a `.xwjson` file
4. Verify:
   - Custom icon appears in Solution Explorer
   - File opens in your custom viewer
   - JSON content displays correctly

## Distribution

1. Build in Release mode
2. The `.vsix` file will be created in `bin\Release\`
3. Users can install by double-clicking the `.vsix` file

## Resources

- [Visual Studio Extensibility Documentation](https://docs.microsoft.com/en-us/visualstudio/extensibility/)
- [VSIX Project Template](https://marketplace.visualstudio.com/items?itemName=VisualStudioProductTeam.VisualStudio2019SDK)
- [Creating a Custom Editor](https://docs.microsoft.com/en-us/visualstudio/extensibility/creating-a-custom-editor)

## Notes

- The Python integration requires `exonware-xwjson` to be installed in the Python environment
- Consider caching decoded JSON for better performance
- Add error handling for missing Python or library
- Consider adding syntax highlighting using a JSON editor component (like AvalonEdit)
