#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
"${REPO_ROOT}/hack/verify-owners.sh"
python3 -m unittest discover -s "${REPO_ROOT}/tools" -p "test_*.py" -v
