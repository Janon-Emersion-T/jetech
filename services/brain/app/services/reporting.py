from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import ReportRecord


REPORT_KINDS = ("critical", "hourly", "daily", "weekly")


def latest_reports_by_kind(db: Session) -> dict:
    reports: dict[str, dict] = {}
    for kind in REPORT_KINDS:
        report = db.scalar(
            select(ReportRecord)
            .where(ReportRecord.kind == kind)
            .order_by(ReportRecord.created_at.desc())
            .limit(1)
        )
        if report:
            reports[kind] = {
                "status": report.status,
                "summary": report.summary,
                "delivery_channel": report.delivery_channel,
            }
    return reports
