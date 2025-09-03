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
- `layouts/partials/header.html` - Custom header with profile avatar
- `static/css/custom.css` - Custom CSS overrides

### How It Works
The custom CSS is loaded by overriding the theme's `head.html` partial. This approach:
1. Creates a custom head partial that includes the theme's original head content
2. Adds a link to the custom CSS file after the theme's styles
3. Uses `!important` declarations to ensure the custom styles override the theme's defaults

## Profile Avatar in Navbar

### Problem
The default theme uses a generic house icon in the navbar logo area.

### Solution
Replaced the house icon with a rounded profile image that:
- Links to the homepage (same functionality as the original icon)
- Displays as a circular avatar (35px on desktop, 30px on mobile)
- Has hover effects (scale and border color change)
- Maintains the same positioning and behavior as the original icon

### Technical Details
- **Custom header partial**: Overrides the theme's header to use an `<img>` tag instead of SVG
- **CSS styling**: Rounded corners, hover effects, and responsive sizing
- **Image path**: Uses `/images/profile.png` (same as the about page)

## Navigation Simplification

### Problem
The default theme had separate "Home" and "Posts" menu items, creating redundancy since the home page can display posts directly.

### Solution
Simplified the navigation by:
- **Removed "Posts" menu item** from the navbar
- **Made "Home" link point to posts page** to preserve the year headers layout
- **Created custom index page** that displays posts with year groupings
- **Streamlined navigation** to just "Home" and "About"

### Technical Details
- **Custom index layout**: Created `layouts/index.html` that displays posts with year groupings
- **Menu structure**: "Home" now points to `/posts/` URL, preserving the year headers layout
- **User experience**: Cleaner navigation while maintaining the organized posts layout with year headers

## Benefits
- ✅ Content width now matches navbar width
- ✅ Better visual alignment and consistency
- ✅ Maintains responsive design
- ✅ Easy to maintain and update
- ✅ No theme file modifications required
- ✅ Personal branding with profile avatar in navbar
- ✅ Professional appearance similar to GitHub profiles
- ✅ Simplified navigation with streamlined menu
- ✅ Direct access to blog posts from home page
- ✅ Preserved year headers layout for organized post display
