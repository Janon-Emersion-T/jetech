# Jarvis v2 Architecture

Jarvis v2 is split by runtime responsibility:

- Python brain: business workflow orchestration, approvals, reporting, decision memory, lifecycle records.
- Rust local core: local execution guard, emergency stop enforcement, future scheduler and file watcher.
- Node automation: browser automation and external web task execution.
- Electron desktop UI: operator control plane only.

This separation keeps AI-heavy logic in Python while moving long-running system-sensitive work into Rust.
