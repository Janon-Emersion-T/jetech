#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOG_DIR="${ROOT_DIR}/runtime/logs"
UI_DIR="${ROOT_DIR}/apps/desktop-ui"

mkdir -p "${LOG_DIR}"

"${ROOT_DIR}/scripts/jarvis-start" --services-only

cd "${UI_DIR}"
unset ELECTRON_RUN_AS_NODE
JARVIS_BRAIN_API_URL="http://127.0.0.1:8000" npm run desktop >>"${LOG_DIR}/desktop-ui.log" 2>&1
