# Jarvis v2

Local-first autonomous business operating system for LKProfessionals (Pvt) Ltd.

## Workspace Layout

- `apps/desktop-ui`: Electron + React + Tailwind operator console
- `services/brain`: Python FastAPI brain API, business memory, approvals, reports
- `services/local-core-rs`: Rust daemon for guarded local execution and emergency control
- `services/automation-node`: Node.js automation layer for Playwright-style browser jobs
- `contracts`: JSON contracts between services
- `deploy`: Docker and K3s deployment templates
- `runtime`: local data, logs, backups, and generated project workspaces

## Quick Start

1. Python brain:
   `cd services/brain && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000`
2. Desktop UI:
   `cd apps/desktop-ui && npm install && npm run app`
3. Rust local core:
   `cd services/local-core-rs && cargo run`
4. Node automation:
   `cd services/automation-node && npm install && npm run dev`

Environment defaults are local-first and point to `127.0.0.1`.
