"""Core Django views: exact 1-to-1 mirror of FastAPI gateway endpoints in backend/services/gateway/app.py.

Preserves exact JSON response shapes and original logic.
Zero login / auth required.
"""
from __future__ import annotations

import json
import mimetypes
from pathlib import Path

from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .clients import manager


def _state() -> dict:
    s = dict(manager.telemetry.clock_state())
    s.pop("source", None)
    return s


def state(request):
    """GET /api/state: demo simulation clock state."""
    return JsonResponse(_state())


@csrf_exempt
def clock(request):
    """POST /api/clock: play | pause | reset | step."""
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body.decode("utf-8")) if request.body else {}
    except Exception:
        data = {}

    action = data.get("action")
    if action not in ("play", "pause", "reset", "step"):
        return JsonResponse({"detail": "action must be play, pause, reset or step"}, status=400)

    try:
        ticks = int(data.get("ticks", 1))
    except (ValueError, TypeError):
        ticks = 1

    seconds_per_tick = data.get("seconds_per_tick")
    if seconds_per_tick is not None:
        try:
            seconds_per_tick = float(seconds_per_tick)
        except (ValueError, TypeError):
            seconds_per_tick = None

    manager.telemetry.clock_action(action, ticks, seconds_per_tick)
    return JsonResponse(_state())


def fridges(request):
    """GET /api/fridges: all fridges with tier, Virtual Vial, risk, cause."""
    s = _state()
    return JsonResponse({"state": s, "fridges": manager.alerts.fleet(s["tick"])})


def fridge_detail(request, fid: str):
    """GET /api/fridges/{fid}?hours=24: one fridge with history and forecast."""
    s = _state()
    t = s["tick"]
    if not manager.alerts.has(fid, t):
        return JsonResponse({"detail": f"unknown fridge {fid}"}, status=404)

    try:
        hours = int(request.GET.get("hours", 24))
    except (ValueError, TypeError):
        hours = 24
    hours = max(1, min(hours, 48))

    return JsonResponse(manager.alerts.detail(fid, t, hours=hours))


def active_alerts(request):
    """GET /api/alerts: active fridges not in Normal tier."""
    s = _state()
    return JsonResponse({
        "state": s,
        "alerts": [f for f in manager.alerts.fleet(s["tick"]) if f["tier"] != "Normal"],
    })


def alert_history(request):
    """GET /api/alerts/history: tier transition events."""
    s = _state()
    fridge_id = request.GET.get("fridge_id")
    return JsonResponse({"state": s, "events": manager.alerts.history(s["tick"], fridge_id)})


def health(request):
    """GET /api/health: health of gateway, telemetry, alerts, and ML inference service."""
    is_http = hasattr(manager.inference, "url")
    out = {
        "gateway": {
            "ok": True,
            "mode": "django",
            "ml_inference_mode": "fastapi_http" if is_http else "in_process",
        }
    }
    for name, c in (("telemetry", manager.telemetry), ("alerts", manager.alerts)):
        try:
            out[name] = c.health()
        except Exception as e:
            out[name] = {"ok": False, "error": str(e)}

    if hasattr(manager.inference, "health"):
        try:
            out["inference"] = manager.inference.health()
        except Exception as e:
            out["inference"] = {"ok": False, "error": str(e)}
    return JsonResponse(out)


def index(request):
    """GET /: serves frontend index.html."""
    index_file = settings.FRONTEND_DIR / "index.html"
    if index_file.is_file():
        return HttpResponse(index_file.read_bytes(), content_type="text/html; charset=utf-8")
    raise Http404("frontend/index.html not found")


def frontend_files(request, path: str):
    """Serves frontend static assets (CSS, JS, images, etc.)."""
    target = (settings.FRONTEND_DIR / path).resolve()
    # Directory traversal security check
    if not str(target).startswith(str(settings.FRONTEND_DIR.resolve())):
        raise Http404("Access denied")

    if target.is_dir() and (target / "index.html").is_file():
        target = target / "index.html"

    if target.is_file():
        mime, _ = mimetypes.guess_type(str(target))
        return HttpResponse(target.read_bytes(), content_type=mime or "application/octet-stream")
    raise Http404(f"File {path} not found")
