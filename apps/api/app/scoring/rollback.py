_ROLLBACK_MARKERS = ("rollback", "revert", "restore", "backout")


def score_rollback_readiness(description: str | None) -> dict[str, object]:
    text = (description or "").lower()
    has_plan = any(marker in text for marker in _ROLLBACK_MARKERS)
    if has_plan:
        return {"score": 100, "missing_items": [], "recommendations": []}
    return {
        "score": 25,
        "missing_items": ["rollback_plan"],
        "recommendations": ["Document how to revert or restore this change before deployment."],
    }
