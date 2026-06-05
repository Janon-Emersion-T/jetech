from sqlalchemy.orm import Session

from app.models.entities import ApprovalRequest, DecisionMemory, Project, ReportRecord, SystemState
from app.services.approvals import STOP_COMMAND
from app.services.decision_memory import find_existing_decision


def build_chat_response(db: Session, message: str) -> str:
    lowered = message.lower()

    if message.strip() == STOP_COMMAND:
        return "Emergency stop command recognized. Use the approvals endpoint or STOP handler to activate the guard."

    existing = find_existing_decision(db, "operations", message)
    if existing:
        return f"Decision memory already has a confirmed answer: {existing.answer}"

    if "approval" in lowered:
        pending = db.query(ApprovalRequest).filter(ApprovalRequest.status == "pending").count()
        return f"There are {pending} pending approval requests requiring strict token confirmation."

    if "project" in lowered or "deployment" in lowered:
        projects = db.query(Project).count()
        return f"Jarvis is tracking {projects} client projects with isolated container, database, ingress, SSL, backup, and log planning."

    if "report" in lowered:
        reports = db.query(ReportRecord).count()
        return f"There are {reports} reports stored for critical, hourly, daily, and weekly delivery workflows."

    emergency = db.query(SystemState).filter(SystemState.key == "emergency_stop").first()
    stop_state = "active" if emergency and emergency.is_active else "ready"
    return (
        "Jarvis v2 is operating in local-first mode. "
        f"Emergency stop is {stop_state}. "
        "Decision memory, approvals, reporting, and project lifecycle records are available through the brain API."
    )
