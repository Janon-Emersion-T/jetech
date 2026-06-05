from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TimestampedMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Customer(TimestampedMixin, Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), unique=True)
    company_name: Mapped[str] = mapped_column(String(160))
    email: Mapped[str] = mapped_column(String(160))
    phone: Mapped[str] = mapped_column(String(60))
    status: Mapped[str] = mapped_column(String(40), default="lead")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    quotations: Mapped[list["Quotation"]] = relationship(back_populates="customer")
    projects: Mapped[list["Project"]] = relationship(back_populates="customer")


class Quotation(TimestampedMixin, Base):
    __tablename__ = "quotations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    reference_code: Mapped[str] = mapped_column(String(60), unique=True)
    summary: Mapped[str] = mapped_column(Text)
    total_amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(12), default="LKR")
    status: Mapped[str] = mapped_column(String(40), default="draft")

    customer: Mapped[Customer] = relationship(back_populates="quotations")


class Project(TimestampedMixin, Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    name: Mapped[str] = mapped_column(String(160), unique=True)
    status: Mapped[str] = mapped_column(String(40), default="active")
    stack: Mapped[str | None] = mapped_column(String(120), nullable=True)
    workspace_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    container_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    database_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    ingress_host: Mapped[str | None] = mapped_column(String(160), nullable=True)
    ssl_status: Mapped[str] = mapped_column(String(40), default="pending")
    demo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    admin_login: Mapped[str | None] = mapped_column(String(255), nullable=True)
    known_issues: Mapped[str | None] = mapped_column(Text, nullable=True)

    customer: Mapped[Customer] = relationship(back_populates="projects")
    domains: Mapped[list["DomainRecord"]] = relationship(back_populates="project")
    hostings: Mapped[list["HostingRecord"]] = relationship(back_populates="project")
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="project")
    deployments: Mapped[list["DeploymentRecord"]] = relationship(back_populates="project")
    backups: Mapped[list["BackupRecord"]] = relationship(back_populates="project")
    grace_periods: Mapped[list["GracePeriodRecord"]] = relationship(back_populates="project")


class DomainRecord(TimestampedMixin, Base):
    __tablename__ = "domains"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    domain_name: Mapped[str] = mapped_column(String(160), unique=True)
    registrar: Mapped[str | None] = mapped_column(String(120), nullable=True)
    renewal_date: Mapped[str | None] = mapped_column(String(40), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="active")

    project: Mapped[Project] = relationship(back_populates="domains")


class HostingRecord(TimestampedMixin, Base):
    __tablename__ = "hostings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    provider: Mapped[str] = mapped_column(String(120))
    environment_type: Mapped[str] = mapped_column(String(40), default="k3s")
    vps_label: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="planned")

    project: Mapped[Project] = relationship(back_populates="hostings")


class Invoice(TimestampedMixin, Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    invoice_number: Mapped[str] = mapped_column(String(60), unique=True)
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(12), default="LKR")
    due_date: Mapped[str | None] = mapped_column(String(40), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="unpaid")

    project: Mapped[Project] = relationship(back_populates="invoices")
    payment_statuses: Mapped[list["PaymentStatusRecord"]] = relationship(back_populates="invoice")


class PaymentStatusRecord(TimestampedMixin, Base):
    __tablename__ = "payment_statuses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"))
    status: Mapped[str] = mapped_column(String(40), default="pending")
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    paid_at: Mapped[str | None] = mapped_column(String(40), nullable=True)

    invoice: Mapped[Invoice] = relationship(back_populates="payment_statuses")


class ApprovalRequest(TimestampedMixin, Base):
    __tablename__ = "approval_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String(32), unique=True)
    action_type: Mapped[str] = mapped_column(String(80))
    action_summary: Mapped[str] = mapped_column(Text)
    risk_level: Mapped[str] = mapped_column(String(40), default="medium")
    target_environment: Mapped[str | None] = mapped_column(String(60), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="pending")
    requested_via: Mapped[str] = mapped_column(String(40), default="whatsapp_pending")
    response_command: Mapped[str | None] = mapped_column(String(120), nullable=True)


class DeploymentRecord(TimestampedMixin, Base):
    __tablename__ = "deployments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    environment: Mapped[str] = mapped_column(String(40), default="staging")
    version_label: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(40), default="planned")
    test_report: Mapped[str | None] = mapped_column(Text, nullable=True)
    seo_report: Mapped[str | None] = mapped_column(Text, nullable=True)
    security_report: Mapped[str | None] = mapped_column(Text, nullable=True)
    performance_score: Mapped[str | None] = mapped_column(String(40), nullable=True)
    deployment_plan: Mapped[str | None] = mapped_column(Text, nullable=True)

    project: Mapped[Project] = relationship(back_populates="deployments")


class BackupRecord(TimestampedMixin, Base):
    __tablename__ = "backups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    backup_type: Mapped[str] = mapped_column(String(40), default="full")
    storage_path: Mapped[str] = mapped_column(String(255))
    retention_until: Mapped[str | None] = mapped_column(String(40), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="scheduled")

    project: Mapped[Project] = relationship(back_populates="backups")


class GracePeriodRecord(TimestampedMixin, Base):
    __tablename__ = "grace_periods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    starts_on: Mapped[str] = mapped_column(String(40))
    ends_on: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(40), default="active")
    archive_policy: Mapped[str] = mapped_column(Text)

    project: Mapped[Project] = relationship(back_populates="grace_periods")


class DecisionMemory(TimestampedMixin, Base):
    __tablename__ = "decision_memory"
    __table_args__ = (UniqueConstraint("normalized_key", name="uq_decision_memory_normalized_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(80))
    normalized_key: Mapped[str] = mapped_column(String(200))
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    decided_by: Mapped[str] = mapped_column(String(80), default="owner")
    confidence: Mapped[str] = mapped_column(String(40), default="confirmed")


class ReportRecord(TimestampedMixin, Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kind: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(40), default="queued")
    summary: Mapped[str] = mapped_column(Text)
    delivery_channel: Mapped[str] = mapped_column(String(40), default="whatsapp_pending")


class SystemState(TimestampedMixin, Base):
    __tablename__ = "system_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(80), unique=True)
    value: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
