"""
Template context available on every page.

Used by the shared sidebar/navbar to highlight the active navigation item
and to show the signed-in user's name without repeating it in every view.
"""

from .data import CURRENT_USER


def portal_context(request):
    return {
        "portal_name": "CampusLink",
        "current_user": CURRENT_USER,
        # URL name of the current view — used for nav highlighting
        "active_nav": getattr(request.resolver_match, "url_name", None),
    }
