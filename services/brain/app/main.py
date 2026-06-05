import json
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.bootstrap import initialize_database, seed_data
from app.db.session import SessionLocal, get_db
from app.models.entities import (
    ApprovalRequest,
    BackupRecord,
    ChatSession,
    Customer,
    DecisionMemory,
    DeploymentRecord,
    DomainRecord,
    GracePeriodRecord,
    HostingRecord,
    Invoice,
    PaymentStatusRecord,
    Project,
    Quotation,
    ReportRecord,
)
from app.schemas.common import MessageResponse
from app.schemas.entities import (
    ApprovalRequestCreate,
    ApprovalResponseCommand,
    ChatRequest,
    ChatSessionCreate,
    ChatSessionRename,
    CustomerCreate,
    DecisionMemoryQuery,
    DecisionMemoryResolve,
    EmergencyStopRequest,
    ProjectCreate,
    PromptTemplatesPayload,
    ReportCreate,
    SocialChannelsPayload,
    SystemModePayload,
)
from app.services.approvals import STOP_COMMAND, apply_response_command, generate_approval_token, get_or_create_emergency_state
from app.services.chat import build_chat_response
from app.services.chat_sessions import (
    append_message,
    create_session,
    delete_session,
    ensure_session,
    list_sessions,
    rename_session,
    serialize_session,
)
from app.services.decision_memory import find_existing_decision, store_decision
from app.services.reporting import latest_reports_by_kind
from app.services.runtime_documents import get_document, set_document


ROOT_DIR = Path(__file__).resolve().parents[3]
CONTRACTS_PATH = ROOT_DIR / "contracts" / "service-contracts.json"

app = FastAPI(title="Jarvis Brain API", version="2.0.0")


@app.on_event("startup")
def startup() -> None:
    initialize_database()
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()


@app.get("/api/v1/health")
def health() -> dict:
    return {"status": "online", "service": "jarvis-brain-api"}


@app.get("/api/v1/contracts")
def contracts() -> dict:
    return json.loads(CONTRACTS_PATH.read_text())


@app.get("/api/v1/system/overview")
def system_overview(db: Session = Depends(get_db)) -> dict:
    emergency_state = get_or_create_emergency_state(db)
    return {
        "customer_count": db.query(Customer).count(),
        "project_count": db.query(Project).count(),
        "pending_approvals": db.query(ApprovalRequest).filter(ApprovalRequest.status == "pending").count(),
        "emergency_stop_active": emergency_state.is_active,
        "reports": latest_reports_by_kind(db),
    }


@app.post("/api/v1/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)) -> dict:
    session = ensure_session(db, request.chat_id)
    append_message(db, session, "user", request.message)
    response = build_chat_response(db, request.message)
    session = append_message(db, session, "jarvis", response)
    return {"chat_id": session.session_key, "response": response, "session": serialize_session(session)}


@app.get("/api/v1/chat/sessions")
def chat_sessions(db: Session = Depends(get_db)) -> dict:
    return {"sessions": list_sessions(db)}


@app.post("/api/v1/chat/sessions")
def new_chat_session(payload: ChatSessionCreate, db: Session = Depends(get_db)) -> dict:
    session = create_session(db, payload.title)
    return {"session": serialize_session(session)}


@app.get("/api/v1/chat/sessions/{session_key}")
def chat_session_detail(session_key: str, db: Session = Depends(get_db)) -> dict:
    session = db.query(ChatSession).filter(ChatSession.session_key == session_key).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return {"session": serialize_session(session)}


@app.post("/api/v1/chat/sessions/{session_key}/rename")
def chat_session_rename(session_key: str, payload: ChatSessionRename, db: Session = Depends(get_db)) -> dict:
    session = rename_session(db, session_key, payload.title)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return {"session": serialize_session(session)}


@app.delete("/api/v1/chat/sessions/{session_key}")
def chat_session_delete(session_key: str, db: Session = Depends(get_db)) -> dict:
    if not delete_session(db, session_key):
        raise HTTPException(status_code=404, detail="Chat session not found")
    return {"ok": True}


@app.get("/api/v1/customers")
def list_customers(db: Session = Depends(get_db)) -> dict:
    items = db.scalars(select(Customer).order_by(Customer.created_at.desc())).all()
    return {"items": [serialize_customer(item) for item in items]}


@app.post("/api/v1/customers")
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)) -> dict:
    item = Customer(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"item": serialize_customer(item)}


@app.get("/api/v1/projects")
def list_projects(db: Session = Depends(get_db)) -> dict:
    items = db.scalars(select(Project).order_by(Project.created_at.desc())).all()
    return {"items": [serialize_project(item) for item in items]}


@app.post("/api/v1/projects")
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)) -> dict:
    if not db.get(Customer, payload.customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")

    item = Project(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"item": serialize_project(item)}


@app.post("/api/v1/decision-memory/query")
def decision_memory_query(payload: DecisionMemoryQuery, db: Session = Depends(get_db)) -> dict:
    existing = find_existing_decision(db, payload.category, payload.question)
    return {
        "found": bool(existing),
        "item": serialize_decision(existing) if existing else None,
    }


@app.post("/api/v1/decision-memory/resolve")
def decision_memory_resolve(payload: DecisionMemoryResolve, db: Session = Depends(get_db)) -> dict:
    item = store_decision(
        db,
        category=payload.category,
        question=payload.question,
        answer=payload.answer,
        decided_by=payload.decided_by,
        confidence=payload.confidence,
    )
    return {"item": serialize_decision(item)}


@app.get("/api/v1/approvals/pending")
def pending_approvals(db: Session = Depends(get_db)) -> dict:
    items = db.scalars(
        select(ApprovalRequest)
        .where(ApprovalRequest.status == "pending")
        .order_by(ApprovalRequest.created_at.desc())
    ).all()
    return {"items": [serialize_approval(item) for item in items]}


@app.post("/api/v1/approvals/request")
def request_approval(payload: ApprovalRequestCreate, db: Session = Depends(get_db)) -> dict:
    item = ApprovalRequest(
        token=generate_approval_token(db),
        action_type=payload.action_type,
        action_summary=payload.action_summary,
        risk_level=payload.risk_level,
        target_environment=payload.target_environment,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"item": serialize_approval(item)}


@app.post("/api/v1/approvals/respond")
def respond_to_approval(payload: ApprovalResponseCommand, db: Session = Depends(get_db)) -> dict:
    result = apply_response_command(db, payload.command_text)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.post("/api/v1/system/emergency-stop")
def emergency_stop(payload: EmergencyStopRequest, db: Session = Depends(get_db)) -> dict:
    if payload.command_text.strip() != STOP_COMMAND:
        raise HTTPException(status_code=400, detail="Invalid emergency stop command.")
    result = apply_response_command(db, payload.command_text)
    return result


@app.get("/api/v1/reports/latest")
def latest_reports(db: Session = Depends(get_db)) -> dict:
    return {"items": latest_reports_by_kind(db)}


@app.get("/api/v1/lifecycle/registry")
def lifecycle_registry(db: Session = Depends(get_db)) -> dict:
    return {
        "customers": db.query(Customer).count(),
        "quotations": db.query(Quotation).count(),
        "projects": db.query(Project).count(),
        "domains": db.query(DomainRecord).count(),
        "hostings": db.query(HostingRecord).count(),
        "invoices": db.query(Invoice).count(),
        "payment_statuses": db.query(PaymentStatusRecord).count(),
        "approvals": db.query(ApprovalRequest).count(),
        "deployments": db.query(DeploymentRecord).count(),
        "backups": db.query(BackupRecord).count(),
        "grace_periods": db.query(GracePeriodRecord).count(),
        "decision_memory": db.query(DecisionMemory).count(),
        "reports": db.query(ReportRecord).count(),
    }


@app.post("/api/v1/reports")
def create_report(payload: ReportCreate, db: Session = Depends(get_db)) -> dict:
    item = ReportRecord(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"item": serialize_report(item)}


@app.get("/api/v1/settings/prompt-templates")
def prompt_templates(db: Session = Depends(get_db)) -> dict:
    return get_document(db, "prompt_templates")


@app.post("/api/v1/settings/prompt-templates")
def save_prompt_templates(payload: PromptTemplatesPayload, db: Session = Depends(get_db)) -> dict:
    return set_document(db, "settings", "prompt_templates", payload.templates)


@app.get("/api/v1/settings/social-channels")
def social_channels(db: Session = Depends(get_db)) -> dict:
    return get_document(db, "social_channels")


@app.post("/api/v1/settings/social-channels")
def save_social_channels(payload: SocialChannelsPayload, db: Session = Depends(get_db)) -> dict:
    return set_document(db, "settings", "social_channels", payload.channels)


@app.get("/api/v1/settings/system-mode")
def system_mode(db: Session = Depends(get_db)) -> dict:
    return get_document(db, "system_mode")


@app.post("/api/v1/settings/system-mode")
def save_system_mode(payload: SystemModePayload, db: Session = Depends(get_db)) -> dict:
    return set_document(db, "settings", "system_mode", payload.settings)


def serialize_customer(item: Customer) -> dict:
    return {
        "id": item.id,
        "name": item.name,
        "company_name": item.company_name,
        "email": item.email,
        "phone": item.phone,
        "status": item.status,
        "notes": item.notes,
    }


def serialize_project(item: Project) -> dict:
    return {
        "id": item.id,
        "customer_id": item.customer_id,
        "name": item.name,
        "status": item.status,
        "stack": item.stack,
        "workspace_path": item.workspace_path,
        "container_name": item.container_name,
        "database_name": item.database_name,
        "ingress_host": item.ingress_host,
        "ssl_status": item.ssl_status,
        "demo_url": item.demo_url,
        "admin_login": item.admin_login,
        "known_issues": item.known_issues,
    }


def serialize_decision(item) -> dict | None:
    if not item:
        return None
    return {
        "id": item.id,
        "category": item.category,
        "question": item.question,
        "answer": item.answer,
        "decided_by": item.decided_by,
        "confidence": item.confidence,
    }


def serialize_approval(item: ApprovalRequest) -> dict:
    return {
        "id": item.id,
        "token": item.token,
        "action_type": item.action_type,
        "action_summary": item.action_summary,
        "risk_level": item.risk_level,
        "target_environment": item.target_environment,
        "status": item.status,
    }


def serialize_report(item: ReportRecord) -> dict:
    return {
        "id": item.id,
        "kind": item.kind,
        "status": item.status,
        "summary": item.summary,
        "delivery_channel": item.delivery_channel,
    }
