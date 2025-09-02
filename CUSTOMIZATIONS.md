# Theme Customizations

This document describes the customizations made to the Hugo Blog Awesome theme.

## Content Width Alignment

### Problem
The original theme had different widths for the navbar and content areas:
- **Navbar width**: 890px (`$wide-size`)
- **Content width**: 720px (`$narrow-size`)

This created a visual misalignment where the content appeared narrower than the navigation bar.

### Solution
Created a custom CSS override in `assets/sass/custom.scss` that:

1. **Overrides the `.wrapper` class** to use the same width as the navbar
2. **Applies to all content areas**:
   - Main content wrapper (`.wrapper`)
   - Post pages (`.wrapper.post`)
   - List pages (`.wrapper.list-page`)
3. **Maintains responsive design** with proper mobile breakpoints

### Technical Details

The custom CSS changes the content width from:
```scss
// Original (narrow)
max-width: calc(720px - (30px * 2)); // = 660px

// Custom (wide, matching navbar)
max-width: calc(890px - (30px * 2)); // = 830px
```

### Files Modified
- `layouts/partials/head.html` - Custom head partial to include CSS
- `static/css/custom.css` - Custom CSS overrides

### How It Works
The custom CSS is loaded by overriding the theme's `head.html` partial. This approach:
1. Creates a custom head partial that includes the theme's original head content
2. Adds a link to the custom CSS file after the theme's styles
3. Uses `!important` declarations to ensure the custom styles override the theme's defaults

## Benefits
- ✅ Content width now matches navbar width
- ✅ Better visual alignment and consistency
- ✅ Maintains responsive design
- ✅ Easy to maintain and update
- ✅ No theme file modifications required
