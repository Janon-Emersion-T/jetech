from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import RuntimeDocument


def get_document(db: Session, key: str, default: dict | None = None) -> dict:
    document = db.scalar(select(RuntimeDocument).where(RuntimeDocument.key == key))
    if not document:
        return default or {}
    return json.loads(document.content)


def set_document(db: Session, category: str, key: str, payload: dict) -> dict:
    document = db.scalar(select(RuntimeDocument).where(RuntimeDocument.key == key))
    content = json.dumps(payload, indent=2, sort_keys=True)
    if not document:
        document = RuntimeDocument(category=category, key=key, content=content)
    else:
        document.category = category
        document.content = content
    db.add(document)
    db.commit()
    db.refresh(document)
    return json.loads(document.content)
