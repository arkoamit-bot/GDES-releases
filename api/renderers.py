"""Standardized API response format for all endpoints."""
from rest_framework.renderers import JSONRenderer


class StandardJSONRenderer(JSONRenderer):
    """Wraps all responses in a standard envelope."""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response") if renderer_context else None
        status_code = response.status_code if response else 200

        if status_code >= 400:
            body = {"status": "error", "code": status_code, "message": _extract_error(data)}
        else:
            body = {"status": "success", "data": data}

        return super().render(body, accepted_media_type, renderer_context)


def _extract_error(data):
    if isinstance(data, dict):
        if "detail" in data:
            return data["detail"]
        if "message" in data:
            return data["message"]
        errors = []
        for field, msgs in data.items():
            if isinstance(msgs, list):
                errors.append(f"{field}: {', '.join(str(m) for m in msgs)}")
            else:
                errors.append(str(msgs))
        return "; ".join(errors) if errors else "Unknown error"
    if isinstance(data, list):
        return "; ".join(str(d) for d in data)
    return str(data) if data else "Unknown error"
