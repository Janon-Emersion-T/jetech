import re
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.entities import ApprovalRequest, SystemState


APPROVAL_RE = re.compile(r"^(APPROVE|REJECT)\s+(JVS-\d{4}-\d{5})$")
STOP_COMMAND = "STOP JARVIS"


def generate_approval_token(db: Session) -> str:
    year = datetime.utcnow().year
    total = db.scalar(select(func.count(ApprovalRequest.id))) or 0
    return f"JVS-{year}-{total + 1:05d}"


def get_or_create_emergency_state(db: Session) -> SystemState:
    state = db.scalar(select(SystemState).where(SystemState.key == "emergency_stop"))
    if state:
        return state
    state = SystemState(key="emergency_stop", value="ready", is_active=False)
    db.add(state)
    db.commit()
    db.refresh(state)
    return state


def apply_response_command(db: Session, command_text: str) -> dict:
    command = command_text.strip()
    if command == STOP_COMMAND:
        state = get_or_create_emergency_state(db)
        state.is_active = True
        state.value = "STOP JARVIS"
        db.add(state)
        db.commit()
        return {"ok": True, "type": "emergency_stop", "status": "active"}

    match = APPROVAL_RE.fullmatch(command)
    if not match:
        return {"ok": False, "message": "Invalid approval command format."}

    action, token = match.groups()
    approval = db.scalar(select(ApprovalRequest).where(ApprovalRequest.token == token))
    if not approval:
        return {"ok": False, "message": "Approval token not found."}

    approval.status = "approved" if action == "APPROVE" else "rejected"
    approval.response_command = command
    db.add(approval)
    db.commit()

    return {"ok": True, "type": "approval", "token": token, "status": approval.status}
