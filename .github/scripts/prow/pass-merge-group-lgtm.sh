#!/usr/bin/env bash
set -euo pipefail

: "${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is required}"
: "${SHA:?SHA is required}"

gh api \
  --method POST \
  "repos/${GITHUB_REPOSITORY}/statuses/${SHA}" \
  -f state="success" \
  -f context="prow/lgtm" \
  -f description="Merge queue entry already passed PR-level prow/lgtm gate"
