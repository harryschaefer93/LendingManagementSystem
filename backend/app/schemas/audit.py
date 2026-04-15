from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: UUID
    loan_id: UUID
    action: str
    previous_status: str | None = None
    new_status: str | None = None
    details: str | None = None
    actor_id: str
    actor_name: str
    timestamp: datetime

    model_config = {"from_attributes": True}
