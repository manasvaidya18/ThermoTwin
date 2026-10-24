"""Serve the static frontend (frontend/: website, phone app) from the same port as the API."""
from __future__ import annotations

import mimetypes

from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseRedirect


def index(request):
    return HttpResponseRedirect("/index.html")


def frontend_file(request, path: str):
    root = settings.FRONTEND_DIR.resolve()
    target = (root / path).resolve()
    if root not in target.parents and target != root:
        raise Http404("not found")
    if target.is_dir() and (target / "index.html").is_file():
        target = target / "index.html"
    if not target.is_file():
        raise Http404("not found")
    mime, _ = mimetypes.guess_type(str(target))
    return HttpResponse(target.read_bytes(), content_type=mime or "application/octet-stream")
