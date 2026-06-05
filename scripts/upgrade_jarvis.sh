#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BRANCH="${1:-main}"

cd "${ROOT_DIR}"

if [[ -d .git ]]; then
  git fetch origin
  git checkout "${BRANCH}"
  git pull --ff-only origin "${BRANCH}"
fi

"${ROOT_DIR}/scripts/install_jarvis.sh"
"${ROOT_DIR}/scripts/migrate_v1_data.py" --apply || true
