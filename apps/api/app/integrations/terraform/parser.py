"""
Terraform / OpenTofu plan JSON parser (Community Edition).

Parses `terraform show -json <planfile>` output to extract ChangedResource records.
No Terraform Cloud API calls — pure JSON transformation.
"""
from __future__ import annotations

from typing import Any

_SKIP_ACTIONS = frozenset({"no-op", "read"})
_STRIP_KEYS = frozenset({"tags_all", "timeouts"})


def parse_plan(plan: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Parse a Terraform plan JSON object.
    Returns list of ChangedResource-compatible dicts.
    Skips no-op and read actions.
    """
    results = []
    for change in plan.get("resource_changes", []):
        actions: list[str] = change.get("change", {}).get("actions", [])
        if not actions or set(actions) <= _SKIP_ACTIONS:
            continue

        provider = change.get("provider_name", "")
        if "/" in provider:
            provider = provider.rsplit("/", 1)[-1]

        results.append(
            {
                "address": change.get("address"),
                "resource_type": change.get("type", ""),
                "provider": provider or None,
                "actions": actions,
                "before_summary": _trim(change.get("change", {}).get("before")),
                "after_summary": _trim(change.get("change", {}).get("after")),
            }
        )
    return results


def _trim(state: dict[str, Any] | None) -> dict[str, Any] | None:
    if state is None:
        return None
    return {
        k: v
        for k, v in state.items()
        if k not in _STRIP_KEYS and not k.endswith("_sensitive")
    }
