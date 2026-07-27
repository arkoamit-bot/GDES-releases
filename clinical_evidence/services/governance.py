"""Governance engine — immutable audit trails for all CEI operations."""

import json
from typing import Any

from clinical_evidence.models import EvidenceAuditLog


def record(
    action: str,
    actor: str = "",
    resource_type: str = "",
    resource_id: str = "",
    payload: dict[str, Any] | None = None,
    knowledge_version: str = "",
) -> EvidenceAuditLog:
    """Record an immutable audit entry."""
    return EvidenceAuditLog.objects.create(
        action=action,
        actor=actor,
        resource_type=resource_type,
        resource_id=resource_id,
        payload=payload or {},
        knowledge_version=knowledge_version,
    )


def record_query(query) -> EvidenceAuditLog:
    return record(
        action="evidence.query",
        resource_type="evidencequery",
        resource_id=query.query_id,
        payload={
            "query_text": query.query_text[:200],
            "disease_id": query.disease_id,
            "result_count": query.result_count,
        },
    )


def record_validation(validation) -> EvidenceAuditLog:
    return record(
        action="recommendation.validate",
        resource_type="recommendationvalidation",
        resource_id=str(validation.pk),
        payload={
            "outcome": validation.outcome,
            "confidence": validation.confidence_score,
            "recommendation": str(validation.gdes_recommendation_id),
        },
    )


def record_conflict(conflict) -> EvidenceAuditLog:
    return record(
        action="evidence.conflict_detected",
        resource_type="evidenceconflict",
        resource_id=str(conflict.pk),
        payload={
            "severity": conflict.severity,
            "conflict_type": conflict.conflict_type,
            "title": conflict.title[:200],
        },
    )


def record_alert(alert) -> EvidenceAuditLog:
    return record(
        action="evidence.alert_created",
        resource_type="evidencealert",
        resource_id=alert.alert_id,
        payload={
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "title": alert.title[:200],
        },
    )


def record_package(package) -> EvidenceAuditLog:
    return record(
        action="evidence.package_created",
        resource_type="evidencepackage",
        resource_id=package.package_id,
        payload={
            "query_id": package.query_id,
            "ai_confidence": package.ai_confidence,
            "supporting_count": package.supporting_results.count(),
            "contradictory_count": package.contradictory_results.count(),
        },
    )


def get_history(
    resource_type: str,
    resource_id: str,
    limit: int = 50,
) -> list[EvidenceAuditLog]:
    return list(
        EvidenceAuditLog.objects.filter(
            resource_type=resource_type,
            resource_id=resource_id,
        ).order_by("-timestamp")[:limit]
    )


def verify_integrity(audit_entry: EvidenceAuditLog) -> bool:
    """Verify that an audit entry's hash matches its payload."""
    from hashlib import sha256

    payload = {
        "action": audit_entry.action,
        "actor": audit_entry.actor,
        "resource": f"{audit_entry.resource_type}:{audit_entry.resource_id}",
        "data": audit_entry.payload,
        "ts": str(audit_entry.timestamp),
    }
    expected = sha256(
        json.dumps(payload, sort_keys=True, default=str).encode()
    ).hexdigest()
    return audit_entry.audit_hash == expected
