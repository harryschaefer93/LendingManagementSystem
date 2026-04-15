import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog


async def write_audit_log(
    db: AsyncSession,
    *,
    loan_id: uuid.UUID,
    action: str,
    actor_id: str,
    actor_name: str,
    previous_status: str | None = None,
    new_status: str | None = None,
    details: str | None = None,
) -> AuditLog:
    entry = AuditLog(
        loan_id=loan_id,
        action=action,
        previous_status=previous_status,
        new_status=new_status,
        details=details,
        actor_id=actor_id,
        actor_name=actor_name,
    )
    db.add(entry)
    await db.flush()
    return entry


async def get_audit_trail(db: AsyncSession, loan_id: uuid.UUID) -> list[AuditLog]:
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.loan_id == loan_id)
        .order_by(AuditLog.timestamp.asc())
    )
    return list(result.scalars().all())
