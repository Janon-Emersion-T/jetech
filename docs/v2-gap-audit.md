# Jarvis v2 Gap Audit

This is an honest gap audit against the observed `v1` application in `/var/www/jarvis`.

## Restored in v2 During This Pass

- standalone local install and launch flow
- user `systemd` services for brain, local core, and automation
- one-command `jarvis-start`, `jarvis-stop`, `jarvis-status`, `jarvis-upgrade`
- optional one-time legacy import instead of runtime dependence on `v1`
- persistent chat session storage and APIs
- persistent prompt templates, social channel settings, and system mode storage
- decision memory, approvals, emergency stop, reporting, and lifecycle models

## Present in v1 But Still Missing or Reduced in v2

### Frontend Capability Gaps

- `LearningPanel`
- `LogsPanel`
- `MemoryPanel`
- `SettingsPanel` parity
- `SocialChannelPanel` parity
- `ToolsPanel`
- `VoicePanel`
- broader project control workflows from `ProjectPanel`

### Backend/API Capability Gaps

- autonomous learning worker and learning catalog controls
- memory search, fact listing, and memory overview APIs
- activity log and summarized operational logs APIs
- model routing, model fallback, performance, and Ollama management APIs
- voice mode control APIs
- project diagnostics and code review endpoints
- weather/location integration APIs
- broad command routing and tool execution APIs from `v1`

### Runtime/Subsystem Gaps

- offline voice stack
- browser automation session management parity
- local image engine parity
- vector memory / semantic memory parity
- live intelligence / knowledge graph / knowledge quality subsystems
- full CRM, finance, SEO, and document-analysis tool surface from `v1`

### Tooling Gaps

`v1` contains about 70 Python tool modules under `tools/`. `v2` currently has the architecture to host them, but not feature parity yet.

High-value missing groups:

- deployment and hosting tools
- browser automation tools
- CRM and tracker memory tools
- financial, invoice, and payroll tools
- website audit and SEO tools
- developer setup, diagnostics, and project analyzers
- desktop control and integration tools

## Priority Restoration Order

1. Memory, logs, learning, and tools APIs
2. Settings and social-channel UI parity
3. Voice stack and command routing parity
4. Browser automation and deployment tooling parity
5. Semantic memory, vector retrieval, and local AI management parity

## Non-Negotiable Standard

`v2` should replace `v1`, not merely coexist beside it. Until the gaps above are closed, `v2` is a stronger architecture base, but not full feature parity.
