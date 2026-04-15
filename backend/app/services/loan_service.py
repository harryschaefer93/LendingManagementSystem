import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.decision import Decision, DecisionType
from app.models.loan import Loan, LoanStatus
from app.schemas.decision import DecisionCreate
from app.schemas.loan import LoanCreate, LoanUpdate
from app.services.audit_service import write_audit_log

# Valid state transitions: {current_status: [allowed_next_statuses]}
VALID_TRANSITIONS: dict[LoanStatus, list[LoanStatus]] = {
    LoanStatus.draft: [LoanStatus.submitted],
    LoanStatus.submitted: [LoanStatus.in_review],
    LoanStatus.in_review: [LoanStatus.approved, LoanStatus.declined],
}


def _check_transition(current: LoanStatus, target: LoanStatus) -> None:
    allowed = VALID_TRANSITIONS.get(current, [])
    if target not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from '{current.value}' to '{target.value}'. "
            f"Allowed transitions from '{current.value}': {[s.value for s in allowed] if allowed else 'none (terminal state)'}.",
        )


async def list_loans(
    db: AsyncSession,
    *,
    status_filter: LoanStatus | None = None,
    loan_officer_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Loan], int]:
    query = select(Loan)
    count_query = select(func.count()).select_from(Loan)

    if status_filter:
        query = query.where(Loan.status == status_filter)
        count_query = count_query.where(Loan.status == status_filter)
    if loan_officer_id:
        query = query.where(Loan.loan_officer_id == loan_officer_id)
        count_query = count_query.where(Loan.loan_officer_id == loan_officer_id)
    if date_from:
        query = query.where(Loan.created_at >= date_from)
        count_query = count_query.where(Loan.created_at >= date_from)
    if date_to:
        query = query.where(Loan.created_at <= date_to)
        count_query = count_query.where(Loan.created_at <= date_to)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Loan.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    loans = list(result.scalars().all())

    return loans, total


async def get_loan(db: AsyncSession, loan_id: uuid.UUID) -> Loan:
    result = await db.execute(select(Loan).where(Loan.id == loan_id))
    loan = result.scalar_one_or_none()
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Loan {loan_id} not found.",
        )
    return loan


async def create_loan(
    db: AsyncSession,
    data: LoanCreate,
    user: dict,
) -> Loan:
    loan = Loan(
        borrower_name=data.borrower_name,
        loan_type=data.loan_type,
        amount=data.amount,
        term_months=data.term_months,
        status=LoanStatus.draft,
        loan_officer_id=user["id"],
        loan_officer_name=user["name"],
    )
    db.add(loan)
    await db.flush()

    await write_audit_log(
        db,
        loan_id=loan.id,
        action="loan_created",
        new_status=LoanStatus.draft.value,
        actor_id=user["id"],
        actor_name=user["name"],
        details=f"Loan created for {data.borrower_name}, type={data.loan_type.value}, amount={data.amount}",
    )

    return loan


async def update_loan(
    db: AsyncSession,
    loan_id: uuid.UUID,
    data: LoanUpdate,
    user: dict,
) -> Loan:
    loan = await get_loan(db, loan_id)
    if loan.status != LoanStatus.draft:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft loans can be edited.",
        )

    changes = []
    for field, value in data.model_dump(exclude_unset=True).items():
        old_value = getattr(loan, field)
        if old_value != value:
            setattr(loan, field, value)
            changes.append(f"{field}: {old_value} → {value}")

    if changes:
        await write_audit_log(
            db,
            loan_id=loan.id,
            action="loan_updated",
            actor_id=user["id"],
            actor_name=user["name"],
            details="; ".join(changes),
        )

    await db.flush()
    return loan


async def submit_loan(db: AsyncSession, loan_id: uuid.UUID, user: dict) -> Loan:
    loan = await get_loan(db, loan_id)
    _check_transition(loan.status, LoanStatus.submitted)

    previous = loan.status.value
    loan.status = LoanStatus.submitted
    await db.flush()

    await write_audit_log(
        db,
        loan_id=loan.id,
        action="status_change",
        previous_status=previous,
        new_status=LoanStatus.submitted.value,
        actor_id=user["id"],
        actor_name=user["name"],
        details="Loan submitted for review",
    )

    return loan


async def start_review(db: AsyncSession, loan_id: uuid.UUID, user: dict) -> Loan:
    loan = await get_loan(db, loan_id)
    _check_transition(loan.status, LoanStatus.in_review)

    previous = loan.status.value
    loan.status = LoanStatus.in_review
    await db.flush()

    await write_audit_log(
        db,
        loan_id=loan.id,
        action="status_change",
        previous_status=previous,
        new_status=LoanStatus.in_review.value,
        actor_id=user["id"],
        actor_name=user["name"],
        details="Review started by underwriter",
    )

    return loan


async def decide_loan(
    db: AsyncSession,
    loan_id: uuid.UUID,
    data: DecisionCreate,
    user: dict,
) -> Loan:
    loan = await get_loan(db, loan_id)
    target_status = LoanStatus.approved if data.decision == DecisionType.approved else LoanStatus.declined
    _check_transition(loan.status, target_status)

    previous = loan.status.value
    loan.status = target_status

    decision = Decision(
        loan_id=loan.id,
        decision=data.decision,
        notes=data.notes,
        conditions=data.conditions,
        underwriter_id=user["id"],
        underwriter_name=user["name"],
    )
    db.add(decision)
    await db.flush()

    await write_audit_log(
        db,
        loan_id=loan.id,
        action="decision_recorded",
        previous_status=previous,
        new_status=target_status.value,
        actor_id=user["id"],
        actor_name=user["name"],
        details=f"Decision: {data.decision.value}. Notes: {data.notes or 'N/A'}",
    )

    return loan
