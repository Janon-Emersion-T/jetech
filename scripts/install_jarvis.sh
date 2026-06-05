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
SYSTEMD_USER_DIR="${HOME}/.config/systemd/user"

mkdir -p "${LAUNCHER_DIR}" "${APP_DIR}" "${SYSTEMD_USER_DIR}" "${ROOT_DIR}/runtime/logs" "${ROOT_DIR}/runtime/backups"

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

cp "${ROOT_DIR}/deploy/systemd/user/"*.service "${SYSTEMD_USER_DIR}/"
cp "${ROOT_DIR}/deploy/systemd/user/"*.target "${SYSTEMD_USER_DIR}/"

systemctl --user daemon-reload
systemctl --user enable jarvis-stack.target >/dev/null 2>&1 || true

for command_name in jarvis-start jarvis-stop jarvis-status jarvis-upgrade jarvis-self-evolve; do
  rm -f "${LAUNCHER_DIR}/${command_name}"
  cat > "${LAUNCHER_DIR}/${command_name}" <<EOF
#!/usr/bin/env bash
exec "${ROOT_DIR}/scripts/${command_name}"
EOF
  chmod +x "${LAUNCHER_DIR}/${command_name}"
done

rm -f "${LAUNCHER_DIR}/jarvis"
cat > "${LAUNCHER_DIR}/jarvis" <<EOF
#!/usr/bin/env bash
exec "${ROOT_DIR}/scripts/jarvis-start"
EOF
chmod +x "${LAUNCHER_DIR}/jarvis"

chmod +x "${ROOT_DIR}/scripts/"*.sh "${ROOT_DIR}/scripts/jarvis-start" "${ROOT_DIR}/scripts/jarvis-stop" "${ROOT_DIR}/scripts/jarvis-status" "${ROOT_DIR}/scripts/jarvis-upgrade" "${ROOT_DIR}/scripts/jarvis-self-evolve" "${ROOT_DIR}/scripts/migrate_v1_data.py"

cat > "${APP_DIR}/jarvis.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=JARVIS
Comment=Local-first autonomous business operating system
Exec=${LAUNCHER_DIR}/jarvis-start
Icon=${ROOT_DIR}/apps/desktop-ui/public/icon.svg
Terminal=false
Categories=Development;Utility;
StartupNotify=true
EOF

echo "Jarvis v2 installed successfully at ${ROOT_DIR}"
