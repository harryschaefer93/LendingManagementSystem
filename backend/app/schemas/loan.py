from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.loan import LoanStatus, LoanType


class LoanCreate(BaseModel):
    borrower_name: str = Field(..., min_length=1, max_length=255)
    loan_type: LoanType
    amount: float = Field(..., gt=0)
    term_months: int = Field(..., gt=0)


class LoanUpdate(BaseModel):
    borrower_name: str | None = Field(None, min_length=1, max_length=255)
    loan_type: LoanType | None = None
    amount: float | None = Field(None, gt=0)
    term_months: int | None = Field(None, gt=0)


class LoanResponse(BaseModel):
    id: UUID
    borrower_name: str
    loan_type: LoanType
    amount: float
    term_months: int
    status: LoanStatus
    loan_officer_id: str | None = None
    loan_officer_name: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class LoanListResponse(BaseModel):
    items: list[LoanResponse]
    total: int
    skip: int
    limit: int


class LoanDetailResponse(LoanResponse):
    documents: list["DocumentResponseInline"] = []
    decision: "DecisionResponseInline | None" = None
    audit_logs: list["AuditLogResponseInline"] = []


class DocumentResponseInline(BaseModel):
    id: UUID
    filename: str
    document_type: str
    content_type: str | None = None
    file_size: int | None = None
    uploaded_by_name: str | None = None
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class DecisionResponseInline(BaseModel):
    id: UUID
    decision: str
    notes: str | None = None
    conditions: str | None = None
    underwriter_name: str | None = None
    decided_at: datetime

    model_config = {"from_attributes": True}


class AuditLogResponseInline(BaseModel):
    id: UUID
    action: str
    previous_status: str | None = None
    new_status: str | None = None
    details: str | None = None
    actor_name: str
    timestamp: datetime

    model_config = {"from_attributes": True}


LoanDetailResponse.model_rebuild()
