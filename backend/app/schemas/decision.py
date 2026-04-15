from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.decision import DecisionType


class DecisionCreate(BaseModel):
    decision: DecisionType
    notes: str | None = None
    conditions: str | None = None


class DecisionResponse(BaseModel):
    id: UUID
    loan_id: UUID
    decision: DecisionType
    notes: str | None = None
    conditions: str | None = None
    underwriter_id: str
    underwriter_name: str | None = None
    decided_at: datetime

    model_config = {"from_attributes": True}
