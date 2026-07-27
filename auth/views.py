"""Vera Health Authentication Views — Manual Browser Integration.

Provides endpoints for:
- Checking authentication status
- Opening Vera website in user's default browser
- Marking connection as complete (user clicked "Continue Verification")
- Disconnecting from Vera
"""
from __future__ import annotations

import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

logger = logging.getLogger("bgddr.vera.auth")

LOGIN = "/login/"


@login_required(login_url=LOGIN)
def vera_auth_status(request):
    """Check Vera Health authentication status.

    Returns JSON with connection state.
    """
    from clinical_evidence.services.vera_auth import get_vera_auth_service

    auth_service = get_vera_auth_service(request)
    return JsonResponse(auth_service.get_auth_status())


@login_required(login_url=LOGIN)
def vera_auth_open(request):
    """Open Vera Health website in the user's default browser.

    Returns JSON with browser status and URL.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    from clinical_evidence.services.vera_auth import get_vera_auth_service

    auth_service = get_vera_auth_service(request)
    state = auth_service.get_state()

    # Detect internet connectivity
    import urllib.request
    try:
        urllib.request.urlopen("https://www.google.com", timeout=5)
    except Exception:
        return JsonResponse({
            "status": "no_internet",
            "message": "Internet connection required for Vera verification.",
        }, status=503)

    result = auth_service.open_vera_website(email=state.email)
    return JsonResponse(result)


@login_required(login_url=LOGIN)
def vera_auth_connect(request):
    """Mark Vera connection as complete.

    Called when the user clicks "Continue Verification" after
    completing login on the Vera website.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get("email", "").strip()
    except (json.JSONDecodeError, AttributeError):
        email = ""

    from clinical_evidence.services.vera_auth import get_vera_auth_service

    auth_service = get_vera_auth_service(request)
    result = auth_service.mark_connected(email=email)
    return JsonResponse(result)


@login_required(login_url=LOGIN)
def vera_auth_disconnect(request):
    """Disconnect from Vera Health (logout)."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    from clinical_evidence.services.vera_auth import get_vera_auth_service

    auth_service = get_vera_auth_service(request)
    auth_service.disconnect()

    return JsonResponse({
        "status": "disconnected",
        "message": "Disconnected from Vera Health.",
    })


@login_required(login_url=LOGIN)
def vera_auth_complete_review(request):
    """Record that the clinician completed a Vera review.

    Expects JSON body with 'patient_id', 'change_level', and optional 'details'.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        patient_id = data.get("patient_id", "")
        change_level = data.get("change_level", "no_changes")
        details = data.get("details", {})
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({"error": "Invalid request body"}, status=400)

    if not patient_id:
        return JsonResponse({"error": "patient_id is required"}, status=400)

    from clinical_evidence.services.vera_auth import get_vera_auth_service

    auth_service = get_vera_auth_service(request)
    result = auth_service.mark_review_completed(
        patient_id=patient_id,
        change_level=change_level,
        details=details,
    )
    return JsonResponse(result)


@login_required(login_url=LOGIN)
def vera_auth_save_response(request):
    """Save the clinician's pasted Vera response.

    Expects JSON body with 'patient_id' and 'vera_response'.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        patient_id = data.get("patient_id", "")
        vera_response = data.get("vera_response", "")
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({"error": "Invalid request body"}, status=400)

    if not patient_id:
        return JsonResponse({"error": "patient_id is required"}, status=400)
    if not vera_response.strip():
        return JsonResponse({"error": "vera_response is required"}, status=400)

    from clinical_evidence.services.vera_auth import get_vera_auth_service

    auth_service = get_vera_auth_service(request)
    result = auth_service.save_vera_response(
        patient_id=patient_id,
        vera_response=vera_response,
    )
    return JsonResponse(result)
