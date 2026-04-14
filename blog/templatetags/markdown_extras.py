from django import template
from django.template.defaultfilters import linebreaksbr
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="markdownify")
def markdownify(value):
    """Render user-authored markdown safely by escaping raw HTML first."""
    if value is None:
        return ""
    safe_source = escape(value)
    try:
        from markdown import markdown

        rendered = markdown(
            safe_source,
            extensions=["extra", "sane_lists", "nl2br"],
            output_format="html5",
        )
    except Exception:
        # Fallback keeps rendering functional even if Markdown isn't installed.
        rendered = linebreaksbr(safe_source)
    return mark_safe(rendered)
