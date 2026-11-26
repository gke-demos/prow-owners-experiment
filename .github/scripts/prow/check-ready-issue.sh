#!/usr/bin/env bash
set -euo pipefail

: "${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is required}"
: "${PR_NUMBER:?PR_NUMBER is required}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
python3 "${REPO_ROOT}/tools/check_ready_issue.py" \
  --repo "${GITHUB_REPOSITORY}" \
  --pr "${PR_NUMBER}"
