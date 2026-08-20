"""
PagerDuty v3 webhook parser (Community Edition).

Parses PagerDuty webhook payloads for IncidentCorrelation ingestion.
No PagerDuty API calls — pure JSON transformation.
"""
from __future__ import annotations

from typing import Any


def parse_incident_webhook(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Parse a PagerDuty v3 webhook payload (may contain multiple events).
    Returns list of IncidentCorrelation-compatible dicts.
    """
    events: list[dict[str, Any]] = payload.get("events") or [payload]
    results = []
    for event in events:
        incident: dict[str, Any] = event.get("data") or event.get("incident") or {}
        if not incident:
            continue
        service: dict[str, Any] = incident.get("service") or {}
        results.append(
            {
                "incident_source": "pagerduty",
                "incident_title": incident.get("title", ""),
                "incident_url": incident.get("html_url"),
                "service_name": service.get("summary") or service.get("name"),
                "severity": incident.get("severity"),
                "started_at": incident.get("created_at"),
                "correlation_reason": f"PagerDuty event: {event.get('event_type', 'unknown')}",
                "confidence": "possible",
                "raw_payload": event,
            }
        )
    return results
