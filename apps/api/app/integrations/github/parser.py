"""
GitHub webhook payload parser (Community Edition).

Parses incoming GitHub webhook JSON — no outbound GitHub API calls.
Extracts PR metadata for DecisionRecord ingestion and CODEOWNERS approval evidence.
"""
from __future__ import annotations

from typing import Any


def parse_pr_event(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Parse a GitHub pull_request webhook payload.
    Returns DecisionRecord-compatible field dict.
    """
    pr = payload.get("pull_request", {})
    repo = payload.get("repository", {})
    head = pr.get("head", {})
    return {
        "title": pr.get("title", ""),
        "description": pr.get("body"),
        "repository": repo.get("full_name"),
        "pr_number": pr.get("number"),
        "pr_url": pr.get("html_url"),
        "author": (pr.get("user") or {}).get("login"),
        "commit_sha": head.get("sha"),
        "environment": None,
    }


def parse_codeowners_review(review: dict[str, Any]) -> dict[str, Any]:
    """
    Parse a GitHub pull_request_review webhook payload.
    Returns ApprovalEvidence-compatible field dict.
    """
    state = review.get("state", "").upper()
    return {
        "source": "github_codeowners",
        "approver": (review.get("user") or {}).get("login"),
        "approved": state == "APPROVED",
        "reason": review.get("body"),
    }
