from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_DEFAULT_RULES = {
    "environment_weights": {"production": 30, "prod": 30, "staging": 10},
    "action_weights": {"delete": 35, "create": 10, "update": 15, "replace": 35},
    "resource_type_weights": {
        "aws_db_instance": 35,
        "aws_rds_cluster": 35,
        "aws_iam_policy": 25,
        "aws_iam_role": 25,
        "aws_security_group": 20,
    },
}


def score_risk(
    *,
    environment: str | None,
    changed_resources: list[dict[str, Any]],
    config_path: str | None = None,
) -> dict[str, Any]:
    rules = _load_rules(config_path)
    score = 0
    reasons: list[str] = []

    env_key = (environment or "").lower()
    env_weight = rules["environment_weights"].get(env_key, 0)
    if env_weight:
        score += env_weight
        reasons.append(f"{env_key} environment")

    for resource in changed_resources:
        actions = resource.get("actions") or []
        for action in actions:
            action_weight = rules["action_weights"].get(action, 0)
            if action_weight:
                score += action_weight
                target = resource.get("address") or resource.get("resource_type")
                reasons.append(f"{action} action on {target}")

        resource_type = resource.get("resource_type") or ""
        type_weight = rules["resource_type_weights"].get(resource_type, 0)
        if type_weight:
            score += type_weight
            reasons.append(f"sensitive resource type {resource_type}")

    capped = min(score, 100)
    return {"score": capped, "severity": _severity(capped), "reasons": list(dict.fromkeys(reasons))}


def _load_rules(config_path: str | None) -> dict[str, dict[str, int]]:
    if not config_path:
        return _DEFAULT_RULES
    path = Path(config_path)
    if not path.exists():
        return _DEFAULT_RULES
    loaded = yaml.safe_load(path.read_text()) or {}
    merged = {key: value.copy() for key, value in _DEFAULT_RULES.items()}
    for key, value in loaded.items():
        if isinstance(value, dict) and key in merged:
            merged[key].update(value)
    return merged


def _severity(score: int) -> str:
    if score >= 80:
        return "critical"
    if score >= 50:
        return "high"
    if score >= 25:
        return "medium"
    return "low"
