import enum
import uuid

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DecisionType(str, enum.Enum):
    approved = "approved"
    declined = "declined"


class Decision(Base):
    __tablename__ = "decisions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    loan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("loans.id"), nullable=False, unique=True
    )
    decision: Mapped[DecisionType] = mapped_column(Enum(DecisionType, name="decision_type_enum"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    conditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    underwriter_id: Mapped[str] = mapped_column(String(255), nullable=False)
    underwriter_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    decided_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

    loan = relationship("Loan", back_populates="decision")
