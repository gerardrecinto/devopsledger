"""
Argo CD sync event parser (Community Edition).

Parses Argo CD application sync webhooks / notification events for DeploymentEvent ingestion.
No Argo CD API calls — pure JSON transformation.
"""
from __future__ import annotations

from typing import Any


def parse_sync_event(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Parse an Argo CD application event payload.
    Handles both the official webhook format and Argo CD notifications format.
    Returns DeploymentEvent-compatible field dict.
    """
    app = payload.get("app", payload)
    spec = app.get("spec", {})
    status = app.get("status", {})
    op_state = status.get("operationState", {})
    sync = status.get("sync", {})

    return {
        "source": "argocd",
        "app_name": (app.get("metadata") or {}).get("name") or payload.get("application"),
        "environment": (spec.get("destination") or {}).get("namespace"),
        "status": op_state.get("phase") or (status.get("health") or {}).get("status"),
        "revision": sync.get("revision") or (op_state.get("syncResult") or {}).get("revision"),
        "raw_payload": payload,
    }
