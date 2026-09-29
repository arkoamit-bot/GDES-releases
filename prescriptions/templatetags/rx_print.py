"""Display-only helpers for the printed prescription."""
from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def soft_breaks(value):
    """Allow a line break after "+" and "/" in long combination strengths
    ("1000 mg+327 mg+500 mg+400 IU") so a narrow column wraps between
    ingredients instead of inside a word. Rendering only: the stored value,
    the issued snapshot and its hash are unchanged.

    <wbr> rather than a zero-width space: the PDF fallback's base fonts have
    no glyph for U+200B and print it as a box.
    """
    text = conditional_escape(value or "")
    return mark_safe(text.replace("+", "+<wbr>").replace("/", "/<wbr>"))
