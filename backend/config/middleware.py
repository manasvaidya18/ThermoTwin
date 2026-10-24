"""No-store caching, so browsers always show the latest model output and frontend files."""
from __future__ import annotations


class NoCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Cache-Control"] = "no-store"
        return response
