#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 "${REPO_ROOT}/tools/ownersgen.py" --root "${REPO_ROOT}"
