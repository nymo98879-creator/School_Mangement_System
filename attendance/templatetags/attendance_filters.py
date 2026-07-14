from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key"""
    if dictionary and key is not None:
        # Convert key to string for lookup
        return dictionary.get(str(key))
    return None


@register.filter
def querystring_exclude(get_dict, exclude):
    """Return a URL-encoded query string rebuilt from a QueryDict,
    omitting the comma-separated list of ``exclude`` keys (e.g.
    ``"page,per_page"``). Used by the unified pagination footer to
    keep sticky filters (search, status, dates, ...) intact while
    only changing the page / rows-per-page params."""
    if not hasattr(get_dict, "copy"):
        return ""
    params = get_dict.copy()
    for key in str(exclude).split(","):
        key = key.strip()
        if key and key in params:
            del params[key]
    return params.urlencode()