"""Serves the frontend single-page app shell."""

import functools
import json
import os

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

MANIFEST_PATH = os.path.join(settings.BASE_DIR, "web-ui", "dist", ".vite", "manifest.json")


def _read_manifest():
    with open(MANIFEST_PATH) as f:
        return json.load(f)


@functools.cache
def _cached_manifest():
    return _read_manifest()


@ensure_csrf_cookie
def spa_index(request):
    """Renders the SPA shell for any non-API route.

    Asset names come from vite's build manifest and are emitted through
    {% static %}, so hashed-manifest storage resolves them correctly in
    production. Also sets the CSRF cookie so the app can make
    authenticated POSTs from its very first render.
    """
    try:
        # In DEBUG, re-read every request so a fresh `bun run build` is
        # picked up without a server restart.
        manifest = _read_manifest() if settings.DEBUG else _cached_manifest()
    except OSError:
        return HttpResponse(
            "<h1>Frontend not built</h1>"
            "<p>Run <code>bun install &amp;&amp; bun run build</code>, or use the vite dev "
            "server (<code>bun run dev</code>) during development.</p>",
            status=503,
        )

    entry = manifest["index.html"]
    context = {
        "entry_js": entry["file"],
        "entry_css": entry.get("css", []),
    }
    return render(request, "spa/index.html", context=context)
