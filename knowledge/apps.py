import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class KnowledgeConfig(AppConfig):
    name = 'knowledge'
    verbose_name = "Knowledge Platform"

    def ready(self):
        # Lazy bootstrap: schedule check to run on first request, not at import time.
        # This avoids DB access during app initialization (fixes M-1).
        from django.db import connection
        if not connection.connection:
            logger.debug("Knowledge bootstrap deferred (no DB connection yet)")
            return

        try:
            from .bootstrap import check_knowledge_base
            health = check_knowledge_base()
            if health.is_healthy:
                logger.info(
                    "Knowledge platform bootstrap: %d/%d checks passed",
                    sum(1 for v in health.checks.values() if v),
                    len(health.checks),
                )
            else:
                logger.warning(
                    "Knowledge platform bootstrap: %d/%d checks passed. "
                    "Errors: %s. Warnings: %s",
                    sum(1 for v in health.checks.values() if v),
                    len(health.checks),
                    "; ".join(health.errors),
                    "; ".join(health.warnings),
                )
        except Exception:
            logger.exception("Knowledge bootstrap validation could not complete")
