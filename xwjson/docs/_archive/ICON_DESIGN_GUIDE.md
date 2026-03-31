# XWJSON Icon Design Guide

## Overview

This guide provides recommendations for designing the custom icon for `.xwjson` files in Visual Studio.

## Design Principles

1. **Distinctive:** Should be easily distinguishable from JSON icons
2. **Recognizable:** Should suggest "extended" or "binary" JSON
3. **Professional:** Clean, modern design that fits Visual Studio aesthetic
4. **Scalable:** Must work at multiple sizes (16x16 to 256x256)

## Color Scheme

### Recommended Colors

- **Primary:** Purple/Violet (#6B46C1, #7C3AED) - Suggests "extended" or "enhanced"
- **Secondary:** Blue (#3B82F6) - If purple doesn't fit your theme
- **Accent:** White or light gray for text/icons

### Why Purple?

- Differentiates from standard JSON (typically blue/green)
- Suggests "premium" or "enhanced" format
- Not commonly used for file type icons
- Professional and modern

## Icon Concepts

### Concept 1: JSON with "XW" Badge
```
[ ] = JSON brackets
XW = Text overlay in corner
```

- Base: Standard JSON icon (curly braces)
- Overlay: Small "XW" badge in corner
- Color: Purple background for badge

### Concept 2: Binary JSON Indicator
```
[ ] = JSON brackets
⚡ = Lightning bolt (suggests speed/binary)
```

- Base: JSON icon
- Overlay: Binary/lightning indicator
- Color: Purple accent

### Concept 3: Extended JSON Symbol
```
{ } = Curly braces
+ = Plus sign (suggests "extended")
```

- Base: JSON braces
- Overlay: Plus sign or "E" for extended
- Color: Purple

### Concept 4: XW Monogram
```
XW = Stylized monogram
[ ] = Subtle JSON brackets in background
```

- Primary: "XW" letters
- Background: Subtle JSON brackets
- Color: Purple gradient

## Recommended Design: Concept 1 (JSON with XW Badge)

### Description
- Standard JSON icon (curly braces `{ }`) in blue/gray
- Small purple badge in top-right corner with "XW" text
- Clean, professional, immediately recognizable

### Implementation

#### For .ico (Visual Studio)
- **16x16:** Simplified version, just purple square with "XW"
- **32x32:** JSON braces + small XW badge
- **48x48:** Full detail
- **256x256:** High detail, can include subtle gradients

#### For .svg (VS Code)
- Vector format, scales automatically
- Use CSS classes for theming support

## Icon Specifications

### Visual Studio (.ico)

**Required Sizes:**
- 16x16 pixels (toolbar, small views)
- 32x32 pixels (default size)
- 48x48 pixels (large views)
- 256x256 pixels (high DPI, properties)

**Format:**
- ICO file with multiple embedded sizes
- 32-bit color with alpha channel
- PNG compression recommended

**Tools:**
- GIMP, Photoshop, or online ICO converters
- Use `ImageMagick` to combine PNGs: `magick convert icon_*.png icon.ico`

### VS Code (.svg)

**Specifications:**
- SVG format (vector)
- ViewBox: `0 0 16 16` (standard VS Code icon size)
- Use `currentColor` for theming support
- Keep it simple (16x16 effective size)

**Example SVG:**
```svg
<svg width="16" height="16" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
  <!-- JSON braces background -->
  <path d="M2 4 L2 12 M4 2 L4 14" stroke="currentColor" stroke-width="1.5" fill="none"/>
  <path d="M14 4 L14 12 M12 2 L12 14" stroke="currentColor" stroke-width="1.5" fill="none"/>
  
  <!-- XW badge -->
  <rect x="9" y="1" width="6" height="6" fill="#6B46C1" rx="1"/>
  <text x="12" y="5" font-family="monospace" font-size="4" fill="white" text-anchor="middle" font-weight="bold">XW</text>
</svg>
```

## Design Tools

### Free Tools
- **GIMP:** Free image editor, can export ICO
- **Inkscape:** Free vector editor for SVG
- **Figma:** Online design tool (free tier)
- **Canva:** Simple icon creation

### Online Tools
- **Favicon.io:** ICO generator
- **RealFaviconGenerator:** Multi-format icon generator
- **CloudConvert:** Format conversion

### Professional Tools
- **Adobe Illustrator:** Vector design
- **Adobe Photoshop:** Raster design
- **Sketch:** Mac-only design tool

## Implementation Steps

1. **Design in vector format first** (SVG or AI)
   - Easier to scale and modify
   - Can export to any size

2. **Create base JSON icon**
   - Simple curly braces `{ }`
   - Or use existing JSON icon as base

3. **Add XW identifier**
   - Badge, overlay, or integrated design
   - Ensure readable at small sizes

4. **Apply color scheme**
   - Purple primary color
   - Ensure good contrast

5. **Export to required formats**
   - ICO for Visual Studio (multiple sizes)
   - SVG for VS Code

6. **Test at different sizes**
   - Verify readability at 16x16
   - Check appearance in dark/light themes

## Testing Checklist

- [ ] Icon is readable at 16x16 pixels
- [ ] Icon is recognizable at 32x32 pixels
- [ ] Icon looks good in dark theme
- [ ] Icon looks good in light theme
- [ ] Icon is distinct from JSON icon
- [ ] Icon fits Visual Studio aesthetic
- [ ] Icon works in Solution Explorer
- [ ] Icon works in file dialogs

## Example Icon Files

### Simple Text-Based Icon (Quick Start)

If you need something immediately, you can create a simple icon:

1. **16x16:** Purple square with white "XW" text
2. **32x32:** Same, but with JSON braces in background
3. **48x48+:** More detailed version

This can be created in 5 minutes using any image editor.

## Resources

- [Visual Studio Icon Guidelines](https://docs.microsoft.com/en-us/visualstudio/extensibility/ux-guidelines/images-and-icons-for-visual-studio)
- [VS Code Icon Guidelines](https://code.visualstudio.com/api/references/contribution-points#contributes.icons)
- [Icon Design Best Practices](https://www.smashingmagazine.com/2016/05/icon-design-best-practices/)

## Quick Reference

**For Visual Studio Extension:**
- Format: `.ico` with multiple sizes
- Sizes: 16, 32, 48, 256
- Color: Purple (#6B46C1) with white text

**For VS Code Extension:**
- Format: `.svg`
- Size: 16x16 viewBox
- Color: Use `currentColor` for theming

**Design:** JSON braces + "XW" badge/overlay
