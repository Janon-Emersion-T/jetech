from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import engine
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
    ReportRecord,
    RuntimeDocument,
)
from app.services.approvals import generate_approval_token, get_or_create_emergency_state


ROOT_DIR = Path(__file__).resolve().parents[4]


def ensure_runtime_defaults(db: Session) -> None:
    if not db.scalar(select(RuntimeDocument).where(RuntimeDocument.key == "prompt_templates")):
        db.add(
            RuntimeDocument(
                category="settings",
                key="prompt_templates",
                content='{"general":"You are JARVIS for LKProfessionals. Answer clearly and act carefully.","coding":"You are JARVIS coding mode. Inspect carefully, avoid assumptions, and prefer safe changes.","fast":"You are JARVIS fast mode. Answer briefly and directly.","long_context":"You are JARVIS long-context mode. Analyze deeply and summarize clearly."}',
            )
        )
    if not db.scalar(select(RuntimeDocument).where(RuntimeDocument.key == "social_channels")):
        db.add(
            RuntimeDocument(
                category="settings",
                key="social_channels",
                content='{"whatsapp":{"enabled":false,"auto_reply":true,"connection_mode":"web","web_session_name":"default","web_headless":true},"facebook":{"enabled":false,"auto_reply":false},"instagram":{"enabled":false,"auto_reply":false},"linkedin":{"enabled":false,"auto_reply":false},"tiktok":{"enabled":false,"auto_reply":false},"email":{"enabled":false,"auto_reply":false}}',
            )
        )
    if not db.scalar(select(RuntimeDocument).where(RuntimeDocument.key == "system_mode")):
        db.add(
            RuntimeDocument(
                category="settings",
                key="system_mode",
                content='{"system_prompt_version":"2.0.0","personality_profile":"corporate-local-first","active_mode":"operations","strict_mode":true,"developer_mode":true,"voice_mode":false}',
            )
        )
    if not db.scalar(select(ChatSession).where(ChatSession.session_key == "bootstrap-session")):
        db.add(ChatSession(session_key="bootstrap-session", title="Welcome"))
    db.commit()


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)


def seed_data(db: Session) -> None:
    if db.scalar(select(Customer).limit(1)):
        ensure_runtime_defaults(db)
        get_or_create_emergency_state(db)
        return

    customer = Customer(
        name="janon",
        company_name="LKProfessionals (Pvt) Ltd",
        email="operations@lkprofessionals.lk",
        phone="+94-000-000000",
        status="active",
        notes="Primary operator account for Jarvis v2.",
    )
    db.add(customer)
    db.flush()

    project = Project(
        customer_id=customer.id,
        name="Jarvis Internal Platform",
        stack="Electron + React + Tailwind, FastAPI, Rust, Node.js",
        workspace_path=str(ROOT_DIR / "runtime" / "projects" / "jarvis-internal-platform"),
        container_name="jarvis-internal-platform",
        database_name="jarvis_internal_platform",
        ingress_host="demo.jarvis.local",
        ssl_status="planned",
        demo_url="https://demo.jarvis.local",
        admin_login="admin@jarvis.local",
        known_issues="WhatsApp delivery bridge is designed but not wired to a live provider yet.",
    )
    db.add(project)
    db.flush()

    invoice = Invoice(
        project_id=project.id,
        invoice_number="INV-2026-0001",
        amount=25000,
        due_date="2026-07-01",
        status="unpaid",
    )
    db.add(invoice)
    db.flush()

    db.add_all(
        [
            DomainRecord(project_id=project.id, domain_name="jarvis.local", registrar="local", renewal_date="2027-06-05"),
            HostingRecord(project_id=project.id, provider="Jarvis VPS", environment_type="k3s", vps_label="planned", status="planned"),
            DeploymentRecord(
                project_id=project.id,
                environment="staging",
                version_label="v2-bootstrap",
                status="planned",
                test_report="Smoke test plan pending automated browser suite.",
                seo_report="Core metadata and sitemap checks pending.",
                security_report="Guarded execution and approval gate designed; external hardening remains.",
                performance_score="TBD",
                deployment_plan="Build locally, validate staging, request approval token, then promote to VPS.",
            ),
            BackupRecord(
                project_id=project.id,
                backup_type="full",
                storage_path=str(ROOT_DIR / "runtime" / "backups" / "jarvis-internal-platform"),
                retention_until="2026-09-05",
                status="scheduled",
            ),
            GracePeriodRecord(
                project_id=project.id,
                starts_on="2026-07-01",
                ends_on="2026-10-01",
                status="policy_defined",
                archive_policy="Service may be disabled after non-payment; backups retained for three months before live deletion.",
            ),
            ReportRecord(kind="critical", status="ready", summary="Critical actions will raise instant WhatsApp-ready summaries."),
            ReportRecord(kind="hourly", status="ready", summary="Hourly active project progress summaries are enabled at the data model level."),
            ReportRecord(kind="daily", status="ready", summary="Daily operational summaries are stored for later WhatsApp dispatch."),
            ReportRecord(kind="weekly", status="ready", summary="Weekly business performance reporting pipeline is scaffolded."),
            RuntimeDocument(
                category="settings",
                key="prompt_templates",
                content='{"general":"You are JARVIS for LKProfessionals. Answer clearly and act carefully.","coding":"You are JARVIS coding mode. Inspect carefully, avoid assumptions, and prefer safe changes.","fast":"You are JARVIS fast mode. Answer briefly and directly.","long_context":"You are JARVIS long-context mode. Analyze deeply and summarize clearly."}',
            ),
            RuntimeDocument(
                category="settings",
                key="social_channels",
                content='{"whatsapp":{"enabled":false,"auto_reply":true,"connection_mode":"web","web_session_name":"default","web_headless":true},"facebook":{"enabled":false,"auto_reply":false},"instagram":{"enabled":false,"auto_reply":false},"linkedin":{"enabled":false,"auto_reply":false},"tiktok":{"enabled":false,"auto_reply":false},"email":{"enabled":false,"auto_reply":false}}',
            ),
            RuntimeDocument(
                category="settings",
                key="system_mode",
                content='{"system_prompt_version":"2.0.0","personality_profile":"corporate-local-first","active_mode":"operations","strict_mode":true,"developer_mode":true,"voice_mode":false}',
            ),
            DecisionMemory(
                category="operations",
                normalized_key="client never receives source code",
                question="Client never receives source code",
                answer="All source code remains owned by LKProfessionals and is not transferred to clients.",
                decided_by="owner",
                confidence="confirmed",
            ),
            ApprovalRequest(
                token=generate_approval_token(db),
                action_type="production_deploy",
                action_summary="Approve first protected production deployment flow for Jarvis-managed client projects.",
                risk_level="high",
                target_environment="production",
                status="pending",
            ),
            PaymentStatusRecord(invoice_id=invoice.id, status="pending", note="Awaiting annual payment settlement."),
        ]
    )

    db.commit()
    ensure_runtime_defaults(db)
    get_or_create_emergency_state(db)
