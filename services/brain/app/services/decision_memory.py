from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import DecisionMemory


def normalize_question(question: str) -> str:
    return " ".join(question.strip().lower().split())


def find_existing_decision(db: Session, category: str, question: str) -> DecisionMemory | None:
    normalized_key = normalize_question(question)
    query = select(DecisionMemory).where(
        DecisionMemory.category == category,
        DecisionMemory.normalized_key == normalized_key,
    )
    return db.scalar(query)


def store_decision(
    db: Session,
    *,
    category: str,
    question: str,
    answer: str,
    decided_by: str,
    confidence: str,
) -> DecisionMemory:
    existing = find_existing_decision(db, category, question)
    normalized_key = normalize_question(question)
    if existing:
        existing.answer = answer
        existing.decided_by = decided_by
        existing.confidence = confidence
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    entry = DecisionMemory(
        category=category,
        normalized_key=normalized_key,
        question=question,
        answer=answer,
        decided_by=decided_by,
        confidence=confidence,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
