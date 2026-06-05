#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
UI_DIR="${ROOT_DIR}/apps/desktop-ui"
BRAIN_DIR="${ROOT_DIR}/services/brain"
CORE_DIR="${ROOT_DIR}/services/local-core-rs"
AUTOMATION_DIR="${ROOT_DIR}/services/automation-node"
LAUNCHER_DIR="${HOME}/.local/bin"
APP_DIR="${HOME}/.local/share/applications"

mkdir -p "${LAUNCHER_DIR}" "${APP_DIR}" "${ROOT_DIR}/runtime/logs" "${ROOT_DIR}/runtime/backups"

cd "${BRAIN_DIR}"
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

cd "${UI_DIR}"
npm install
npm run build

cd "${AUTOMATION_DIR}"
npm install

cd "${CORE_DIR}"
cargo build

cat > "${LAUNCHER_DIR}/jarvis" <<EOF
#!/usr/bin/env bash
exec "${ROOT_DIR}/scripts/run_jarvis_desktop.sh"
EOF
chmod +x "${LAUNCHER_DIR}/jarvis"

cat > "${APP_DIR}/jarvis.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=JARVIS
Comment=Local-first autonomous business operating system
Exec=${LAUNCHER_DIR}/jarvis
Icon=${ROOT_DIR}/apps/desktop-ui/public/icon.svg
Terminal=false
Categories=Development;Utility;
StartupNotify=true
EOF

echo "Jarvis v2 installed successfully at ${ROOT_DIR}"
