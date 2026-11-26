#!/usr/bin/env python3
"""Enforces that pull requests link an open issue labeled `ready-for-pr`.

Matches the Agent Substrate contribution workflow (#3922 / PR #4055):
- Every PR (including Drafts) must reference an issue in its description using
  `Fixes #NNN` (or Closes/Resolves) or `Part of #NNN`.
- HTML comments (`<!-- ... -->`) and fenced code blocks are stripped first so
  PR template comments never false-match.
- At least one referenced issue must exist in the same repository, be an actual
  Issue (not a Pull Request), be OPEN, and carry the `ready-for-pr` label.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from typing import Callable


REQUIRED_LABEL = "ready-for-pr"
EXEMPT_AUTHORS = {"dependabot[bot]"}

HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
FENCED_CODE_RE = re.compile(r"(?ms)^[ \t]*(?:```|~~~).*?^[ \t]*(?:```|~~~)[^\n]*")


def strip_ignored_blocks(body: str) -> str:
    cleaned = HTML_COMMENT_RE.sub("", body or "")
    cleaned = FENCED_CODE_RE.sub("", cleaned)
    return cleaned


def extract_linked_issues(body: str, repo: str) -> list[int]:
    """Extracts issue numbers referenced via Fixes/Closes/Resolves or Part of."""
    cleaned = strip_ignored_blocks(body)
    escaped_repo = re.escape(repo)
    pattern = re.compile(
        r"\b(?:fix(?:e[sd])?|close[sd]?|resolve[sd]?|part\s+of)\s*:?\s+"
        rf"(?:#|https://github\.com/{escaped_repo}/issues/|{escaped_repo}#)(\d+)\b",
        re.IGNORECASE,
    )
    seen: set[int] = set()
    ordered: list[int] = []
    for match in pattern.finditer(cleaned):
        num = int(match.group(1))
        if num not in seen:
            seen.add(num)
            ordered.append(num)
    return ordered


def gh_api_json(endpoint: str, method: str = "GET", fields: dict[str, str] | None = None) -> dict:
    cmd = ["gh", "api", "--method", method, endpoint]
    if fields:
        for key, val in fields.items():
            cmd.extend(["-f", f"{key}={val}"])
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"gh api {endpoint} failed ({proc.returncode}): {proc.stderr.strip()}")
    return json.loads(proc.stdout) if proc.stdout.strip() else {}


def evaluate_pr(
    pr_body: str,
    pr_author: str,
    repo: str,
    fetch_issue: Callable[[int], dict | None],
) -> tuple[bool, str]:
    if pr_author in EXEMPT_AUTHORS:
        return True, f"Author {pr_author} is exempt."

    issue_nums = extract_linked_issues(pr_body, repo)
    if not issue_nums:
        return (
            False,
            "No linked issue (`Fixes #NNN` or `Part of #NNN`) was found in the PR description.",
        )

    reasons: list[str] = []
    for num in issue_nums:
        issue = fetch_issue(num)
        if issue is None:
            reasons.append(f"`#{num}` does not exist in `{repo}`.")
            continue
        if "pull_request" in issue:
            reasons.append(f"`#{num}` is a pull request, not an issue.")
            continue
        if str(issue.get("state", "")).lower() != "open":
            reasons.append(f"`#{num}` is closed (`state={issue.get('state')}`).")
            continue
        labels = {
            str(lbl.get("name", "")).lower()
            for lbl in issue.get("labels", [])
            if isinstance(lbl, dict)
        }
        if REQUIRED_LABEL not in labels:
            reasons.append(f"`#{num}` does not carry the `{REQUIRED_LABEL}` label yet.")
            continue
        return True, f"Verified open `{REQUIRED_LABEL}` issue #{num}."

    joined = " ".join(reasons)
    return False, joined


def build_close_comment(repo: str, reason: str) -> str:
    ready_url = f"https://github.com/{repo}/issues?q=state%3Aopen+label%3A{REQUIRED_LABEL}"
    return (
        "Thank you for your interest in contributing!\n\n"
        f"Every pull request (including drafts and small fixes) must link an open issue "
        f"carrying the [`{REQUIRED_LABEL}`]({ready_url}) label in its description using "
        "`Fixes #NNN` or `Part of #NNN`.\n\n"
        f"**Why this PR was closed:** {reason}\n\n"
        "### How to reopen this PR\n"
        f"1. Discuss the change on an issue first and wait for an area owner or maintainer to apply `{REQUIRED_LABEL}`.\n"
        "2. Edit this PR's description above to include `Fixes #NNN` (or `Part of #NNN`).\n"
        "3. Comment `/reopen` on this thread and Prow will reopen the PR automatically."
    )


def write_github_output(allowed: bool) -> None:
    out_path = os.environ.get("GITHUB_OUTPUT")
    val = "true" if allowed else "false"
    if out_path:
        with open(out_path, "a", encoding="utf-8") as fh:
            fh.write(f"allowed={val}\n")
    print(f"allowed={val}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--pr", required=True, type=int, help="Pull request number")
    args = parser.parse_args()

    pr = gh_api_json(f"repos/{args.repo}/pulls/{args.pr}")
    if str(pr.get("state", "")).lower() != "open":
        print(f"PR #{args.pr} is already closed; skipping.")
        write_github_output(False)
        return 0

    body = str(pr.get("body") or "")
    author = str((pr.get("user") or {}).get("login") or "")

    def fetch_issue(num: int) -> dict | None:
        try:
            return gh_api_json(f"repos/{args.repo}/issues/{num}")
        except RuntimeError:
            return None

    allowed, reason = evaluate_pr(body, author, args.repo, fetch_issue)
    print(f"PR #{args.pr} ({author}): allowed={allowed} ({reason})")

    if not allowed:
        comment = build_close_comment(args.repo, reason)
        gh_api_json(
            f"repos/{args.repo}/issues/{args.pr}/comments",
            method="POST",
            fields={"body": comment},
        )
        gh_api_json(
            f"repos/{args.repo}/pulls/{args.pr}",
            method="PATCH",
            fields={"state": "closed"},
        )

    write_github_output(allowed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
