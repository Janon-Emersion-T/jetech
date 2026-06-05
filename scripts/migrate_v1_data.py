#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, UTC
from pathlib import Path
import site
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
V1_STORAGE = Path("/var/www/jarvis/storage")
RUNTIME_DIR = ROOT_DIR / "runtime"
ARCHIVE_DIR = RUNTIME_DIR / "imports" / "v1"
BACKUP_DIR = RUNTIME_DIR / "backups"
VENV_SITE_PACKAGES = next((ROOT_DIR / "services" / "brain" / ".venv" / "lib").glob("python*/site-packages"), None)

if VENV_SITE_PACKAGES and VENV_SITE_PACKAGES.exists():
    site.addsitedir(str(VENV_SITE_PACKAGES))
sys.path.insert(0, str(ROOT_DIR / "services" / "brain"))

from app.core.bootstrap import initialize_database
from app.db.session import SessionLocal
from app.models.entities import Customer, DecisionMemory, Project
from app.services.decision_memory import store_decision


SELECTED_FILES = [
    "chat_sessions.json",
    "project_registry.json",
    "recent_projects.json",
    "prompt_templates.json",
    "social_channels.json",
    "current_location.json",
    "current_project.json",
    "system_mode.json",
    "ui_activity_log.jsonl",
    "autonomous_learning_state.json",
]

SELECTED_DATABASES = ["memory.db", "cognitive_engine.db"]


def load_json(path: Path):
    return json.loads(path.read_text()) if path.exists() else None


def ensure_default_customer(db) -> Customer:
    customer = db.query(Customer).filter(Customer.company_name == "LKProfessionals (Pvt) Ltd").first()
    if customer:
        return customer

    customer = Customer(
        name="janon",
        company_name="LKProfessionals (Pvt) Ltd",
        email="operations@lkprofessionals.lk",
        phone="+94-000-000000",
        status="active",
        notes="Auto-created during v1 to v2 migration.",
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def snapshot_selected_data(timestamp: str) -> dict:
    destination = ARCHIVE_DIR / timestamp
    destination.mkdir(parents=True, exist_ok=True)

    copied = []
    for relative_name in SELECTED_FILES + SELECTED_DATABASES:
        source = V1_STORAGE / relative_name
        if not source.exists():
            continue
        target = destination / relative_name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append(relative_name)

    manifest = {
        "source": str(V1_STORAGE),
        "copied_at": timestamp,
        "copied_items": copied,
    }
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def import_projects(db) -> list[str]:
    imported = []
    staged_names: set[str] = set()
    staged_paths: set[str] = set()
    registry = load_json(V1_STORAGE / "project_registry.json") or {}
    customer = ensure_default_customer(db)

    for project_name, payload in registry.items():
        existing = db.query(Project).filter(Project.name == project_name).first()
        if existing or project_name in staged_names:
            continue
        project = Project(
            customer_id=customer.id,
            name=project_name,
            status="active",
            stack="legacy-import",
            workspace_path=payload.get("path"),
            known_issues="Imported from Jarvis v1 registry.",
        )
        db.add(project)
        imported.append(project_name)
        staged_names.add(project_name)
        if payload.get("path"):
            staged_paths.add(payload["path"])

    recent_projects = load_json(V1_STORAGE / "recent_projects.json") or []
    for item in recent_projects:
        path = item.get("path")
        if not path:
            continue
        name = Path(path).name
        if name in staged_names or path in staged_paths:
            continue
        existing = (
            db.query(Project)
            .filter((Project.workspace_path == path) | (Project.name == name))
            .first()
        )
        if existing:
            continue
        project = Project(
            customer_id=customer.id,
            name=name,
            status="archived",
            stack="legacy-import",
            workspace_path=path,
            known_issues=f"Imported from v1 recent projects; last used {item.get('used_at')}.",
        )
        db.add(project)
        imported.append(name)
        staged_names.add(name)
        staged_paths.add(path)

    db.commit()
    return imported


def import_decisions(db) -> list[str]:
    imported = []
    prompt_templates = load_json(V1_STORAGE / "prompt_templates.json") or {}
    system_mode = load_json(V1_STORAGE / "system_mode.json") or {}
    current_project = load_json(V1_STORAGE / "current_project.json") or {}
    social_channels = load_json(V1_STORAGE / "social_channels.json") or {}

    decisions = [
        (
            "prompting",
            "Preferred general Jarvis prompt template",
            prompt_templates.get("general"),
        ),
        (
            "prompting",
            "Preferred coding Jarvis prompt template",
            prompt_templates.get("coding"),
        ),
        (
            "operations",
            "Current active mode from Jarvis v1",
            system_mode.get("active_mode"),
        ),
        (
            "operations",
            "Current project selected in Jarvis v1",
            current_project.get("path"),
        ),
        (
            "integrations",
            "WhatsApp connection mode in Jarvis v1",
            (social_channels.get("whatsapp") or {}).get("connection_mode"),
        ),
    ]

    for category, question, answer in decisions:
        if not answer:
            continue
        store_decision(
            db,
            category=category,
            question=question,
            answer=str(answer),
            decided_by="v1_migration",
            confidence="imported",
        )
        imported.append(question)
    return imported


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate selected Jarvis v1 data into v2.")
    parser.add_argument("--apply", action="store_true", help="Apply the migration.")
    args = parser.parse_args()

    if not V1_STORAGE.exists():
        print("v1 storage not found, skipping migration.")
        return 0

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    manifest = snapshot_selected_data(timestamp)

    initialize_database()
    db = SessionLocal()
    try:
        imported_projects = import_projects(db) if args.apply else []
        imported_decisions = import_decisions(db) if args.apply else []
    finally:
        db.close()

    summary = {
        "archived_items": manifest["copied_items"],
        "imported_projects": imported_projects,
        "imported_decisions": imported_decisions,
    }
    migration_log = BACKUP_DIR / f"v1-migration-{timestamp}.json"
    migration_log.parent.mkdir(parents=True, exist_ok=True)
    migration_log.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
