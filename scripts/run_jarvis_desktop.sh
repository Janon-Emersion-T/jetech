#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
UI_DIR="${ROOT_DIR}/apps/desktop-ui"
BRAIN_DIR="${ROOT_DIR}/services/brain"
CORE_DIR="${ROOT_DIR}/services/local-core-rs"
AUTOMATION_DIR="${ROOT_DIR}/services/automation-node"
LOG_DIR="${ROOT_DIR}/runtime/logs"
CORE_BIN="${CORE_DIR}/target/debug/jarvis-local-core"

mkdir -p "${LOG_DIR}"

if [[ ! -x "${BRAIN_DIR}/.venv/bin/python" ]]; then
  echo "Brain virtualenv is missing. Run ${ROOT_DIR}/scripts/install_jarvis.sh first." >&2
  exit 1
fi

if [[ ! -x "${UI_DIR}/node_modules/.bin/electron" ]]; then
  echo "Electron is missing. Run ${ROOT_DIR}/scripts/install_jarvis.sh first." >&2
  exit 1
fi

if [[ ! -f "${UI_DIR}/dist/index.html" ]]; then
  echo "Desktop build is missing. Run ${ROOT_DIR}/scripts/install_jarvis.sh first." >&2
  exit 1
fi

BRAIN_PYTHON="${BRAIN_DIR}/.venv/bin/python"
ELECTRON_BIN="${UI_DIR}/node_modules/.bin/electron"
BRAIN_LOG="${LOG_DIR}/brain-api.log"
CORE_LOG="${LOG_DIR}/local-core.log"
AUTOMATION_LOG="${LOG_DIR}/automation-node.log"

cleanup() {
  for pid_var in ELECTRON_PID BRAIN_PID CORE_PID AUTOMATION_PID; do
    pid="${!pid_var:-}"
    if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
      kill "${pid}" 2>/dev/null || true
      wait "${pid}" 2>/dev/null || true
    fi
  done
}

trap cleanup EXIT

cd "${CORE_DIR}"
if [[ -x "${CORE_BIN}" ]]; then
  "${CORE_BIN}" >"${CORE_LOG}" 2>&1 &
else
  cargo run >"${CORE_LOG}" 2>&1 &
fi
CORE_PID=$!

cd "${AUTOMATION_DIR}"
node src/server.js >"${AUTOMATION_LOG}" 2>&1 &
AUTOMATION_PID=$!

cd "${BRAIN_DIR}"
"${BRAIN_PYTHON}" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 >"${BRAIN_LOG}" 2>&1 &
BRAIN_PID=$!

for _ in $(seq 1 40); do
  if "${BRAIN_PYTHON}" - <<'PY' >/dev/null 2>&1
import urllib.request
urllib.request.urlopen("http://127.0.0.1:8000/api/v1/health", timeout=1)
PY
  then
    break
  fi
  sleep 0.5
done

cd "${UI_DIR}"
JARVIS_BRAIN_API_URL="http://127.0.0.1:8000" "${ELECTRON_BIN}" --no-sandbox .
ELECTRON_PID=$!
wait "${ELECTRON_PID}"
