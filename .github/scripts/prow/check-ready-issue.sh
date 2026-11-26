#!/usr/bin/env bash
set -euo pipefail

: "${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is required}"
: "${PR_NUMBER:?PR_NUMBER is required}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
EXTRA_ARGS=()
if [[ "${REOPEN_ATTEMPT:-false}" == "true" ]]; then
  EXTRA_ARGS+=(--reopen-attempt)
fi

python3 "${REPO_ROOT}/tools/check_ready_issue.py" \
  --repo "${GITHUB_REPOSITORY}" \
  --pr "${PR_NUMBER}" \
  "${EXTRA_ARGS[@]}"
