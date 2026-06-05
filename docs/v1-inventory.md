# Jarvis v1 Inventory

Observed in `/var/www/jarvis` without modifying it:

## Existing Frontend

- `frontend/`: React + Vite + Electron desktop shell
- `frontend/src/panels`: dashboard, chat, projects, learning, memory, tools, logs, settings, voice, social channels
- `frontend/src/services`: API client modules for chat, memory, models, logs, system, tools, voice
- `frontend/electron`: Electron entry and preload bridge

## Existing Python Core

- `api_server.py`: FastAPI API surface
- `main.py` and `run.py`: startup orchestration
- `core/`: memory, chat, routing, tool registry, autonomous learning, activity logs, model routing
- `tools/`: large Python tool catalog including browser automation, backups, CRM, reports, deployment, Linux admin, SEO, and web development helpers
- `voice/`: offline voice mode, speech-to-text, Piper TTS, wake word, voice state

## Existing Data and Runtime State

- `storage/`: local memory DBs, logs, browser sessions, learning catalogs, integrations, screenshots
- `config/` and `data/`: model catalogs and learning manifests
- `tests/` plus root test files: targeted capability checks

## v2 Refactor Direction

- Preserve the desktop control-plane concept from the React + Electron shell.
- Keep AI orchestration in Python.
- Move guarded background execution responsibilities to Rust.
- Move browser automation responsibilities to Node.js.
- Replace scattered operational state with explicit business lifecycle models, approval controls, and decision memory.
