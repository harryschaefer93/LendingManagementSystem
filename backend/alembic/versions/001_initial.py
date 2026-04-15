"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2026-04-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enum types are created automatically by SQLAlchemy metadata via model imports in env.py
    # Define references for use in table columns (create_type=False prevents duplicate creation)
    loan_type_enum = sa.Enum("mortgage", "refinance", "personal", "commercial", name="loan_type_enum", create_type=False)
    loan_status_enum = sa.Enum("draft", "submitted", "in_review", "approved", "declined", name="loan_status_enum", create_type=False)
    document_type_enum = sa.Enum("id", "income_proof", "property", name="document_type_enum", create_type=False)
    decision_type_enum = sa.Enum("approved", "declined", name="decision_type_enum", create_type=False)

    # Loans table
    op.create_table(
        "loans",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("borrower_name", sa.String(255), nullable=False),
        sa.Column("loan_type", loan_type_enum, nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("term_months", sa.Integer(), nullable=False),
        sa.Column("status", loan_status_enum, server_default="draft"),
        sa.Column("loan_officer_id", sa.String(255), nullable=True),
        sa.Column("loan_officer_name", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Documents table
    op.create_table(
        "documents",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("loan_id", UUID(as_uuid=True), sa.ForeignKey("loans.id"), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("document_type", document_type_enum, nullable=False),
        sa.Column("blob_url", sa.String(1024), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("uploaded_by", sa.String(255), nullable=True),
        sa.Column("uploaded_by_name", sa.String(255), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Decisions table
    op.create_table(
        "decisions",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("loan_id", UUID(as_uuid=True), sa.ForeignKey("loans.id"), nullable=False, unique=True),
        sa.Column("decision", decision_type_enum, nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("conditions", sa.Text(), nullable=True),
        sa.Column("underwriter_id", sa.String(255), nullable=False),
        sa.Column("underwriter_name", sa.String(255), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Audit Logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("loan_id", UUID(as_uuid=True), sa.ForeignKey("loans.id"), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("previous_status", sa.String(50), nullable=True),
        sa.Column("new_status", sa.String(50), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("actor_id", sa.String(255), nullable=False),
        sa.Column("actor_name", sa.String(255), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("decisions")
    op.drop_table("documents")
    op.drop_table("loans")

    sa.Enum(name="decision_type_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="document_type_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="loan_status_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="loan_type_enum").drop(op.get_bind(), checkfirst=True)
