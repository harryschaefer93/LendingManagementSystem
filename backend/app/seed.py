"""
Seed data for the LMS POC.
Run with: python -m app.seed
"""

import asyncio
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, engine
from app.models.audit import AuditLog
from app.models.decision import Decision, DecisionType
from app.models.loan import Loan, LoanStatus, LoanType


OFFICER_1 = {"id": "officer-1", "name": "Jane Smith"}
OFFICER_2 = {"id": "officer-2", "name": "Michael Chen"}
UNDERWRITER_1 = {"id": "underwriter-1", "name": "Sarah Johnson"}
UNDERWRITER_2 = {"id": "underwriter-2", "name": "David Park"}

NOW = datetime.now(timezone.utc)


def _ts(days_ago: int, hours: int = 0) -> datetime:
    return NOW - timedelta(days=days_ago, hours=hours)


SEED_LOANS = [
    # 2 Draft
    {
        "borrower_name": "Robert Williams",
        "loan_type": LoanType.mortgage,
        "amount": 450000.00,
        "term_months": 360,
        "status": LoanStatus.draft,
        "officer": OFFICER_1,
        "created": _ts(1),
    },
    {
        "borrower_name": "Emily Davis",
        "loan_type": LoanType.personal,
        "amount": 25000.00,
        "term_months": 60,
        "status": LoanStatus.draft,
        "officer": OFFICER_2,
        "created": _ts(0, 6),
    },
    # 2 Submitted
    {
        "borrower_name": "James Thompson",
        "loan_type": LoanType.refinance,
        "amount": 320000.00,
        "term_months": 240,
        "status": LoanStatus.submitted,
        "officer": OFFICER_1,
        "created": _ts(5),
    },
    {
        "borrower_name": "Maria Garcia",
        "loan_type": LoanType.commercial,
        "amount": 750000.00,
        "term_months": 120,
        "status": LoanStatus.submitted,
        "officer": OFFICER_2,
        "created": _ts(3),
    },
    # 2 In Review
    {
        "borrower_name": "Christopher Lee",
        "loan_type": LoanType.mortgage,
        "amount": 580000.00,
        "term_months": 360,
        "status": LoanStatus.in_review,
        "officer": OFFICER_1,
        "created": _ts(10),
    },
    {
        "borrower_name": "Patricia Brown",
        "loan_type": LoanType.refinance,
        "amount": 290000.00,
        "term_months": 180,
        "status": LoanStatus.in_review,
        "officer": OFFICER_2,
        "created": _ts(8),
    },
    # 4 Approved
    {
        "borrower_name": "Daniel Martinez",
        "loan_type": LoanType.mortgage,
        "amount": 425000.00,
        "term_months": 360,
        "status": LoanStatus.approved,
        "officer": OFFICER_1,
        "created": _ts(30),
    },
    {
        "borrower_name": "Jennifer Wilson",
        "loan_type": LoanType.personal,
        "amount": 15000.00,
        "term_months": 36,
        "status": LoanStatus.approved,
        "officer": OFFICER_2,
        "created": _ts(25),
    },
    {
        "borrower_name": "Andrew Taylor",
        "loan_type": LoanType.commercial,
        "amount": 1200000.00,
        "term_months": 120,
        "status": LoanStatus.approved,
        "officer": OFFICER_1,
        "created": _ts(20),
    },
    {
        "borrower_name": "Lisa Anderson",
        "loan_type": LoanType.refinance,
        "amount": 350000.00,
        "term_months": 240,
        "status": LoanStatus.approved,
        "officer": OFFICER_2,
        "created": _ts(15),
    },
    # 2 Declined
    {
        "borrower_name": "Kevin Thomas",
        "loan_type": LoanType.commercial,
        "amount": 2000000.00,
        "term_months": 60,
        "status": LoanStatus.declined,
        "officer": OFFICER_1,
        "created": _ts(22),
    },
    {
        "borrower_name": "Amanda Jackson",
        "loan_type": LoanType.mortgage,
        "amount": 800000.00,
        "term_months": 360,
        "status": LoanStatus.declined,
        "officer": OFFICER_2,
        "created": _ts(18),
    },
]


async def _create_audit_trail(
    db: AsyncSession,
    loan_id: uuid.UUID,
    loan_data: dict,
) -> None:
    """Create realistic audit trail entries matching the loan's final status."""
    officer = loan_data["officer"]
    created = loan_data["created"]
    status = loan_data["status"]

    # All loans start as created
    db.add(AuditLog(
        loan_id=loan_id,
        action="loan_created",
        new_status="draft",
        actor_id=officer["id"],
        actor_name=officer["name"],
        details=f"Loan created for {loan_data['borrower_name']}",
        timestamp=created,
    ))

    if status == LoanStatus.draft:
        return

    # Submitted
    submit_time = created + timedelta(hours=2)
    db.add(AuditLog(
        loan_id=loan_id,
        action="status_change",
        previous_status="draft",
        new_status="submitted",
        actor_id=officer["id"],
        actor_name=officer["name"],
        details="Loan submitted for review",
        timestamp=submit_time,
    ))

    if status == LoanStatus.submitted:
        return

    # In Review
    review_time = submit_time + timedelta(days=1)
    underwriter = UNDERWRITER_1 if loan_data["officer"] == OFFICER_1 else UNDERWRITER_2
    db.add(AuditLog(
        loan_id=loan_id,
        action="status_change",
        previous_status="submitted",
        new_status="in_review",
        actor_id=underwriter["id"],
        actor_name=underwriter["name"],
        details="Review started by underwriter",
        timestamp=review_time,
    ))

    if status == LoanStatus.in_review:
        return

    # Decision
    decide_time = review_time + timedelta(days=2)
    decision_value = "approved" if status == LoanStatus.approved else "declined"
    db.add(AuditLog(
        loan_id=loan_id,
        action="decision_recorded",
        previous_status="in_review",
        new_status=decision_value,
        actor_id=underwriter["id"],
        actor_name=underwriter["name"],
        details=f"Decision: {decision_value}",
        timestamp=decide_time,
    ))


async def _create_decision(
    db: AsyncSession,
    loan_id: uuid.UUID,
    loan_data: dict,
) -> None:
    """Create decision record for approved/declined loans."""
    underwriter = UNDERWRITER_1 if loan_data["officer"] == OFFICER_1 else UNDERWRITER_2
    status = loan_data["status"]

    if status == LoanStatus.approved:
        db.add(Decision(
            loan_id=loan_id,
            decision=DecisionType.approved,
            notes="All documentation verified. Borrower meets qualification criteria.",
            conditions="Standard insurance required. Property appraisal valid for 90 days.",
            underwriter_id=underwriter["id"],
            underwriter_name=underwriter["name"],
            decided_at=loan_data["created"] + timedelta(days=3, hours=2),
        ))
    elif status == LoanStatus.declined:
        db.add(Decision(
            loan_id=loan_id,
            decision=DecisionType.declined,
            notes="Debt-to-income ratio exceeds threshold. Insufficient collateral documentation.",
            underwriter_id=underwriter["id"],
            underwriter_name=underwriter["name"],
            decided_at=loan_data["created"] + timedelta(days=3, hours=2),
        ))


async def seed() -> None:
    async with async_session() as db:
        # Check if data already exists
        result = await db.execute(select(Loan).limit(1))
        if result.scalar_one_or_none():
            print("Seed data already exists. Skipping.")
            return

        print("Seeding database...")
        for loan_data in SEED_LOANS:
            loan = Loan(
                borrower_name=loan_data["borrower_name"],
                loan_type=loan_data["loan_type"],
                amount=loan_data["amount"],
                term_months=loan_data["term_months"],
                status=loan_data["status"],
                loan_officer_id=loan_data["officer"]["id"],
                loan_officer_name=loan_data["officer"]["name"],
                created_at=loan_data["created"],
            )
            db.add(loan)
            await db.flush()

            await _create_audit_trail(db, loan.id, loan_data)

            if loan_data["status"] in (LoanStatus.approved, LoanStatus.declined):
                await _create_decision(db, loan.id, loan_data)

        await db.commit()
        print(f"Seeded {len(SEED_LOANS)} loans with audit trails and decisions.")


if __name__ == "__main__":
    asyncio.run(seed())
