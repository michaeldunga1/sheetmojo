import re
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


@register.filter(name="excerpt")
def excerpt(value, length=120):
    """
    Extract a plain-text excerpt from markdown content.
    Strips markdown syntax and HTML tags, then truncates to specified length.
    """
    if not value:
        return ""
    
    # Remove markdown images ![alt](url)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', value)
    # Remove markdown links [text](url)
    text = re.sub(r'\[(.+?)\]\(.*?\)', r'\1', text)
    # Remove markdown bold/italic **text** or *text*
    text = re.sub(r'\*{1,2}(.*?)\*{1,2}', r'\1', text)
    # Remove markdown headers #, ##, etc
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    # Remove markdown code blocks ```
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Remove inline code `code`
    text = re.sub(r'`(.+?)`', r'\1', text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Collapse multiple spaces/newlines
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Truncate to length
    if len(text) > length:
        text = text[:length].rsplit(' ', 1)[0] + '…'
    
    return text
