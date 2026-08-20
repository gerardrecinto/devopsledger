"""
GitHub webhook payload parser (Community Edition).

Parses incoming GitHub webhook JSON - no outbound GitHub API calls.
Extracts PR metadata for DecisionRecord ingestion and CODEOWNERS approval evidence.
"""
from __future__ import annotations

import fnmatch
import re
from typing import Any

_JIRA_KEY_RE = re.compile(r"\b[A-Z][A-Z0-9]+-\d+\b")


def parse_pr_event(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Parse a GitHub pull_request webhook payload.
    Returns DecisionRecord-compatible field dict.
    """
    pr = payload.get("pull_request") or {}
    repo = payload.get("repository") or {}
    head = pr.get("head") or {}
    return {
        "title": pr.get("title", ""),
        "description": pr.get("body"),
        "repository": repo.get("full_name"),
        "pr_number": pr.get("number"),
        "pr_url": pr.get("html_url"),
        "author": (pr.get("user") or {}).get("login"),
        "commit_sha": head.get("sha"),
        "environment": None,
        "jira_issues": parse_jira_issue_keys(pr.get("body") or ""),
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


def parse_jira_issue_keys(text: str | None) -> list[str]:
    if not text:
        return []
    return list(dict.fromkeys(_JIRA_KEY_RE.findall(text)))


def check_codeowners_approval(
    changed_files: list[str],
    codeowners_text: str | None,
    reviews: list[dict[str, Any]],
) -> dict[str, Any]:
    owners = _matching_owners(changed_files, codeowners_text or "")
    approved_users = {
        ((review.get("user") or {}).get("login") or "").lstrip("@")
        for review in reviews
        if (review.get("state") or "").upper() == "APPROVED"
    }
    approved_owner = next(
        (owner for owner in owners if owner.lstrip("@") in approved_users),
        None,
    )

    owner = approved_owner.lstrip("@") if approved_owner else None
    first_required_owner = owners[0].lstrip("@") if owners else None

    return {
        "source": "github_codeowners",
        "owner": owner or first_required_owner,
        "approver": owner,
        "required": bool(owners),
        "approved": approved_owner is not None,
        "reason": (
            "Matched CODEOWNERS approval"
            if approved_owner
            else "No matching CODEOWNERS approval"
        ),
    }


def _matching_owners(changed_files: list[str], codeowners_text: str) -> list[str]:
    matched: list[str] = []
    for raw_line in codeowners_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        pattern, owners = parts[0], parts[1:]
        normalized_pattern = pattern.lstrip("/")
        for changed_file in changed_files:
            if fnmatch.fnmatch(changed_file, normalized_pattern):
                matched.extend(owners)
                break
    return list(dict.fromkeys(matched))
