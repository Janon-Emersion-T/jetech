from __future__ import annotations

from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import ChatMessage, ChatSession


def serialize_message(message: ChatMessage) -> dict:
    return {
        "id": message.id,
        "role": message.role,
        "text": message.text,
        "created_at": message.created_at.isoformat(),
    }


def serialize_session(session: ChatSession) -> dict:
    return {
        "id": session.session_key,
        "title": session.title,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
        "messages": [serialize_message(message) for message in session.messages],
    }


def list_sessions(db: Session) -> list[dict]:
    sessions = db.scalars(select(ChatSession).order_by(ChatSession.updated_at.desc())).all()
    return [serialize_session(session) for session in sessions]


def get_session(db: Session, session_key: str) -> ChatSession | None:
    return db.scalar(select(ChatSession).where(ChatSession.session_key == session_key))


def create_session(db: Session, title: str | None = None) -> ChatSession:
    session = ChatSession(session_key=str(uuid4()), title=title or "New Chat")
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def ensure_session(db: Session, session_key: str | None) -> ChatSession:
    if session_key:
        existing = get_session(db, session_key)
        if existing:
            return existing
    return create_session(db)


def append_message(db: Session, session: ChatSession, role: str, text: str) -> ChatSession:
    if session.title == "New Chat" and role == "user":
        session.title = text.strip()[:80] or session.title
        db.add(session)

    message = ChatMessage(session_id=session.id, role=role, text=text)
    db.add(message)
    db.commit()
    db.refresh(session)
    return session


def rename_session(db: Session, session_key: str, title: str) -> ChatSession | None:
    session = get_session(db, session_key)
    if not session:
        return None
    session.title = title
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def delete_session(db: Session, session_key: str) -> bool:
    session = get_session(db, session_key)
    if not session:
        return False
    db.delete(session)
    db.commit()
    return True
