import sys
import os
import time
import traceback
import platform
import logging

from django.utils import timezone

from bgddr.version import __version__ as app_version
from knowledge.kb_version import PACKAGED_KB_VERSION

logger = logging.getLogger(__name__)


class FeedbackMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()

        try:
            response = self.get_response(request)
            return response
        except Exception:
            self._log_crash(request)
            raise
        finally:
            elapsed = (time.time() - start) * 1000
            self._log_performance(request, elapsed)

    def _log_crash(self, request):
        try:
            from .models import CrashReport
            from .services.deduplicator import record_error
            from .services.diagnostics import collect_request_context

            exc_type, exc_value, tb = sys.exc_info()
            patient_id = getattr(request, "patient_id", None) or request.GET.get("patient") or request.POST.get("patient")
            encounter_id = getattr(request, "encounter_id", None)
            stack = traceback.format_exc()

            CrashReport.objects.create(
                exception_type=exc_type.__name__ if exc_type else "Unknown",
                exception_message=str(exc_value)[:2000] if exc_value else "",
                stack_trace=stack[:5000],
                module=request.resolver_match.view_name if request.resolver_match else request.path,
                patient_id_hash=self._hash(patient_id),
                encounter_id_hash=self._hash(encounter_id),
                url=request.build_absolute_uri()[:1000],
                workflow=request.session.get("current_workflow", ""),
                app_version=app_version,
                knowledge_version=PACKAGED_KB_VERSION,
            )

            # Also record in the deduplication system for GitHub upload
            try:
                context = collect_request_context(request)
                record_error(
                    exc_type=exc_type.__name__ if exc_type else "Unknown",
                    exc_message=str(exc_value)[:2000] if exc_value else "",
                    stack_trace=stack[:10000],
                    severity="error",
                    context=context,
                )
            except Exception:
                pass
        except Exception as e:
            logger.exception("Failed to log crash report: %s", e)

    def _log_performance(self, request, elapsed_ms):
        try:
            from .models import PerformanceLog

            if elapsed_ms > 2000:
                path = request.path
                if not self._should_skip(path):
                    PerformanceLog.objects.create(
                        metric_name="slow_page",
                        duration_ms=elapsed_ms,
                        module=request.resolver_match.view_name if request.resolver_match else path,
                        page=path[:500],
                        url=request.build_absolute_uri()[:1000],
                        user=request.user if request.user.is_authenticated else None,
                        metadata={
                            "method": request.method,
                            "status": 200,
                        },
                    )
        except Exception as e:
            logger.exception("Failed to log performance: %s", e)

    def _hash(self, value):
        if value is None:
            return ""
        import hashlib
        return hashlib.sha256(str(value).encode()).hexdigest()[:16]

    def _should_skip(self, path):
        skip_prefixes = ("/static/", "/media/", "/admin/jsi18n/", "/health/")
        return any(path.startswith(p) for p in skip_prefixes)
