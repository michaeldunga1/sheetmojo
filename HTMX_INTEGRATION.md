# HTMX Single-Page Application Integration

This Django blog application now uses **HTMX** to provide a smooth single-page application (SPA) experience without full-page reloads.

## What is HTMX?

HTMX is a lightweight JavaScript library that allows you to access AJAX, WebSockets, and Server-Sent Events directly in HTML, enabling modern browser interactions without writing JavaScript. It works seamlessly with server-side rendering frameworks like Django.

## Key Features Implemented

### 1. **Navigation without Page Reloads**
- All navigation links in the navbar use `hx-boost="true"` 
- Navigation between channels, posts, profiles, and the feed happens via AJAX
- The page content updates smoothly without browser refresh

### 2. **Pagination with HTMX**
- Pagination links throughout the application use `hx-boost="true"`
- Moving between pages loads only the new content
- Page state is maintained in the URL query parameters

### 3. **Link Transitions**
- Smooth fade transitions between page loads (200ms animation)
- Visual feedback during content loading
- No jarring full-page refreshes

### 4. **Compatible with Django Forms**
- Form submissions work naturally with HTMX
- POST requests (follow/unfollow, delete operations) work as expected
- CSRF protection is maintained

## File Structure

### Core Files Modified
- **blog/templates/blog/base.html** - Added HTMX script and styling
- **blog/htmx_utils.py** - Utility functions for handling HTMX requests
- **blog/templates/blog/channel_list.html** - Updated with hx-boost
- **blog/templates/blog/post_list.html** - Updated with hx-boost
- **blog/templates/blog/following_posts.html** - Updated with hx-boost
- **blog/templates/blog/profile.html** - Updated with hx-boost

### New Content Templates
- **blog/templates/blog/channel_list_content.html** - Content-only template
- **blog/templates/blog/post_list_content.html** - Content-only template
- **blog/templates/blog/following_posts_content.html** - Content-only template

## How It Works

1. **hx-boost="true"** attribute on links and forms intercepts clicks/submissions
2. HTMX sends an AJAX request to the URL instead of a full page navigation
3. The server returns the full HTML page (with navbar and content)
4. HTMX replaces the target element (the main content section) with the new content
5. CSS transitions provide smooth visual feedback

### Content Area
The main content area in `base.html` is defined as:
```html
<section class="section" id="main-content" hx-target="this" hx-swap="outerHTML">
```

This tells HTMX to:
- Use `this` section as the default target for AJAX requests
- Swap the outer HTML of the section with the new content

## CSS Transitions

The base template includes CSS for smooth fade-in/fade-out transitions:
```css
.htmx-swapping {
  opacity: 0;
  transition: opacity 200ms ease-out;
}
```

This creates a subtle fade effect when content is replaced.

## Usage Examples

### Navigation Links
All navigation links use HTMX boost:
```html
<a href="{% url 'blog:channel-list' %}" hx-boost="true">Channels</a>
```

### Form Submissions
Forms work with HTMX automatically:
```html
<form method="post" action="{% url 'blog:channel-follow' %}" hx-boost="true">
  {% csrf_token %}
  <button type="submit">Follow</button>
</form>
```

### Pagination
Pagination links use HTMX:
```html
<a href="?page={{ page }}" hx-boost="true">Next</a>
```

## Browser Compatibility

HTMX works with all modern browsers (Chrome, Firefox, Safari, Edge) that support:
- ES6
- Fetch API
- MutationObserver

## Performance Benefits

1. **Reduced Data Transfer** - Only new content is fetched via AJAX
2. **No JavaScript Framework Bloat** - HTMX is only ~14KB
3. **Better User Experience** - Smooth, responsive navigation
4. **SEO Friendly** - Server-side rendering is preserved
5. **Progressive Enhancement** - Works without JavaScript (fallback to full page loads)

## Future Enhancements

Potential improvements you could add:
1. **Inline HTMX for Quick Actions** - Use HTMX swaps for follow/unfollow buttons without page reload
2. **History Support** - Add `hx-push-url="true"` for proper browser history
3. **Loading Indicators** - Use HTMX events for custom loading states
4. **Real-time Updates** - Combine with WebSockets for live feed updates
5. **Lazy Loading** - Load images and content on scroll

## Configuration

The HTMX library is loaded from CDN in `base.html`:
```html
<script src="https://unpkg.com/htmx.org@1.9.10" crossorigin="anonymous"></script>
```

To customize HTMX behavior, add configuration in the same file:
```html
<script>
  htmx.config.defaultIndicatorStyle = "spinner";
  htmx.config.timeout = 10000;
</script>
```

## Resources

- [HTMX Official Documentation](https://htmx.org/)
- [HTMX with Django](https://htmx.org/examples/tabs-hateoas/)
- [Browser History Management](https://htmx.org/attributes/hx-push-url/)
