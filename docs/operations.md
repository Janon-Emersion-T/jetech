# Operations

## Start and Stop

- `jarvis-start`: starts the backend stack via user `systemd` and launches the desktop UI in the background.
- `jarvis-stop`: stops the desktop UI and the backend stack.
- `jarvis-status`: shows the user `systemd` status for the backend services.
- `jarvis-upgrade`: pulls, reinstalls, migrates selected v1 data, and restarts the backend stack.
- `jarvis-self-evolve`: writes a self-review/evolution task file into `runtime/data/evolution/`.

## User Services

Installed user units:

- `jarvis-local-core.service`
- `jarvis-automation.service`
- `jarvis-brain.service`
- `jarvis-stack.target`

Use:

```bash
systemctl --user start jarvis-stack.target
systemctl --user stop jarvis-stack.target
systemctl --user status jarvis-brain.service
```

## v1 Migration

Selected data from `/var/www/jarvis/storage` is archived into `runtime/imports/v1/<timestamp>/` and useful state is imported into v2:

- project registry
- recent projects
- prompt templates
- social channel configuration
- current project
- current location
- system mode
- chat session archive
- memory and cognitive engine SQLite files as raw archives
