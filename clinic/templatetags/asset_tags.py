"""Cache-busting static asset helper.

The desktop/pilot build serves compiled assets (e.g. css/app.css) under a fixed
filename via WhiteNoise's CompressedStaticFilesStorage, which does not hash
filenames. Browsers therefore cache app.css indefinitely and miss CSS rebuilds
until a manual hard refresh.

``static_v`` appends ``?v=<mtime>`` (the source file's modification time) to the
static URL. When the asset is rebuilt its mtime changes, so the URL changes and
the browser fetches the new copy — automatically, in both dev (runserver) and
the packaged pilot, with no manifest or collectstatic ordering to manage.
"""
from __future__ import annotations

import os

from django import template
from django.contrib.staticfiles import finders
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def static_v(path: str) -> str:
    """Return the static URL for ``path`` with a cache-busting ``?v=<mtime>`` suffix.

    The asset's modification time is read on each call (a cheap ``stat``), so a
    CSS/JS rebuild takes effect immediately without a server restart. Falls back
    to the plain static URL if the file cannot be located.
    """
    url = static(path)
    version = ""
    abs_path = finders.find(path)
    if abs_path and os.path.exists(abs_path):
        try:
            version = str(int(os.path.getmtime(abs_path)))
        except OSError:
            version = ""
    if version:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}v={version}"
    return url
