"""
Utilities for handling HTMX requests in Django views
"""


def is_htmx_request(request):
    """Check if the request is from HTMX (hx-boost or direct HTMX request)"""
    return request.headers.get('HX-Request') == 'true'


def get_template_name(view_name, is_partial=None):
    """
    Get the appropriate template name based on whether it's a partial request.
    
    Args:
        view_name: Base template name (e.g., 'blog/channel_list.html')
        is_partial: If True, returns partial template. If None/False, returns full template.
    
    Returns:
        Template name string
    """
    if is_partial and '.' in view_name:
        base, ext = view_name.rsplit('.', 1)
        return f"{base}_partial.{ext}"
    return view_name


def render_with_htmx(request, template_name, context=None, full_template=None):
    """
    Helper to render either full page or partial based on HTMX request.
    
    Args:
        request: The request object
        template_name: Partial template name
        context: Context dict
        full_template: Full page template (defaults to base extending template_name)
    
    Returns:
        Tuple of (template_name, context)
    """
    if context is None:
        context = {}
    
    if is_htmx_request(request):
        return template_name, context
    
    if full_template:
        return full_template, context
    
    # By default, return the full template (views should extend base.html)
    return template_name, context
