"""Template helpers for rendering Django Paginator pages.

Replaces the unmaintained django-bootstrap-pagination package with Django's
own Paginator (see kegweb/_pagination.html for the Bootstrap 3 markup).
"""

from django import template

register = template.Library()


@register.simple_tag
def elided_page_range(page, on_each_side=2, on_ends=1):
    """Return a windowed page range (with ELLIPSIS markers) for a Page."""
    return page.paginator.get_elided_page_range(
        page.number, on_each_side=on_each_side, on_ends=on_ends
    )
