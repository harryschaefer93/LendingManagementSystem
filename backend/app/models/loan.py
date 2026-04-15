import enum
import uuid

from sqlalchemy import DateTime, Enum, Integer, Numeric, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LoanType(str, enum.Enum):
    mortgage = "mortgage"
    refinance = "refinance"
    personal = "personal"
    commercial = "commercial"


class LoanStatus(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    in_review = "in_review"
    approved = "approved"
    declined = "declined"


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    borrower_name: Mapped[str] = mapped_column(String(255), nullable=False)
    loan_type: Mapped[LoanType] = mapped_column(Enum(LoanType, name="loan_type_enum"), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    term_months: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[LoanStatus] = mapped_column(
        Enum(LoanStatus, name="loan_status_enum"), default=LoanStatus.draft, server_default="draft"
    )
    loan_officer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    loan_officer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    documents = relationship("Document", back_populates="loan", lazy="selectin")
    decision = relationship("Decision", back_populates="loan", uselist=False, lazy="selectin")
    audit_logs = relationship("AuditLog", back_populates="loan", lazy="selectin", order_by="AuditLog.timestamp")
