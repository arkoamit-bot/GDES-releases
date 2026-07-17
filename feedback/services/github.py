"""GitHub Issue integration — creates and updates issues for critical errors
via the GitHub REST API. Uses only stdlib (urllib) to avoid extra deps."""
from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request

from django.utils import timezone

logger = logging.getLogger(__name__)

_API_BASE = "https://api.github.com"


def _headers(token: str) -> dict:
    h = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "GDES-ErrorReporter/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def _api_call(method: str, url: str, token: str, data: dict | None = None) -> dict | None:
    """Make a GitHub API call. Returns parsed JSON or None on failure."""
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(
        url, data=body, headers=_headers(token), method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body_text = ""
        try:
            body_text = exc.read().decode("utf-8", errors="replace")[:500]
        except Exception:
            pass
        logger.warning("GitHub API %s %s → %s: %s", method, url, exc.code, body_text)
        return None
    except Exception as exc:
        logger.warning("GitHub API call failed: %s", exc)
        return None


def _build_issue_title(occ) -> str:
    """Build a concise issue title from an ErrorOccurrence."""
    mod = occ.module or "unknown"
    return f"[{occ.severity.upper()}] {occ.exception_type} in {mod}"


def _build_issue_body(occ) -> str:
    """Build a rich issue body with all diagnostic info."""
    sections = [
        f"## Error: `{occ.exception_type}`",
        "",
        f"**Module:** `{occ.module}` / `{occ.function_name}` (line {occ.line_number or '?'})",
        f"**Severity:** {occ.severity}",
        f"**Occurrences:** {occ.occurrence_count}",
        f"**First seen:** {occ.first_seen:%Y-%m-%d %H:%M UTC}",
        f"**Last seen:** {occ.last_seen:%Y-%m-%d %H:%M UTC}",
        "",
        "### Message",
        f"```{occ.exception_message[:500]}```",
        "",
        "### Stack Trace",
        f"<details><summary>Click to expand</summary>",
        f"",
        f"```python",
        f"{occ.stack_trace[:4000]}",
        f"```",
        f"</details>",
        "",
        "### Environment",
        f"| Field | Value |",
        f"|-------|-------|",
        f"| GDES Version | `{occ.app_version}` |",
        f"| Python | `{occ.python_version}` |",
        f"| OS | `{occ.os_version}` |",
        f"| Django | `{occ.django_version}` |",
        "",
    ]

    if occ.sample_context:
        sections.extend([
            "### Request Context (sanitized)",
            "```json",
            json.dumps(occ.sample_context, indent=2, default=str)[:2000],
            "```",
            "",
        ])

    sections.extend([
        "---",
        f"*Auto-reported by GDES Error Reporting System*",
        f"*Fingerprint: `{occ.fingerprint}`*",
    ])
    return "\n".join(sections)


def _build_issue_labels(occ) -> list[str]:
    labels = ["bug", "auto-reported", "desktop"]
    if occ.severity == "critical":
        labels.append("critical")
    elif occ.severity == "error":
        labels.append("production")
    return labels


def create_or_update_issue(occ, repo: str, token: str) -> dict | None:
    """Create a new GitHub issue for a new error, or update an existing one
    with occurrence count. Returns the API response or None."""
    if occ.github_issue_number:
        return _update_existing_issue(occ, repo, token)
    return _create_new_issue(occ, repo, token)


def _create_new_issue(occ, repo: str, token: str) -> dict | None:
    url = f"{_API_BASE}/repos/{repo}/issues"
    data = {
        "title": _build_issue_title(occ),
        "body": _build_issue_body(occ),
        "labels": _build_issue_labels(occ),
    }
    result = _api_call("POST", url, token, data)
    if result and "number" in result:
        occ.github_issue_number = result["number"]
        occ.github_issue_url = result.get("html_url", "")
        occ.last_upload_attempt = timezone.now()
        occ.upload_fail_count = 0
        occ.save(update_fields=[
            "github_issue_number", "github_issue_url",
            "last_upload_attempt", "upload_fail_count",
        ])
        logger.info("Created GitHub issue #%s for %s", result["number"], occ.fingerprint[:12])
    else:
        occ.last_upload_attempt = timezone.now()
        occ.upload_fail_count += 1
        occ.save(update_fields=["last_upload_attempt", "upload_fail_count"])
    return result


def _update_existing_issue(occ, repo: str, token: str) -> dict | None:
    """Add a comment to an existing issue with updated occurrence count."""
    url = f"{_API_BASE}/repos/{repo}/issues/{occ.github_issue_number}/comments"
    body = (
        f"**Updated:** {occ.last_seen:%Y-%m-%d %H:%M UTC}\n"
        f"**Occurrences:** {occ.occurrence_count}\n"
        f"**GDES Version:** `{occ.app_version}`\n"
    )
    data = {"body": body}
    result = _api_call("POST", url, token, data)
    occ.last_upload_attempt = timezone.now()
    if result:
        occ.upload_fail_count = 0
    else:
        occ.upload_fail_count += 1
    occ.save(update_fields=["last_upload_attempt", "upload_fail_count"])
    return result


def check_rate_limit(repo: str, token: str) -> dict | None:
    """Check remaining GitHub API rate limit."""
    url = f"{_API_BASE}/rate_limit"
    return _api_call("GET", url, token)
