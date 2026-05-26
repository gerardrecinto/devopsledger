from __future__ import annotations

from typing import Any


def parse_generic_incident(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "incident_source": payload.get("source") or "generic",
        "incident_title": payload.get("title") or payload.get("incident_title") or "",
        "incident_url": payload.get("url") or payload.get("incident_url"),
        "service_name": payload.get("service_name") or payload.get("service"),
        "environment": payload.get("environment"),
        "severity": payload.get("severity"),
        "started_at": payload.get("started_at"),
        "correlation_reason": (
            payload.get("correlation_reason") or "Matched incident webhook fields"
        ),
        "raw_payload": payload,
    }
