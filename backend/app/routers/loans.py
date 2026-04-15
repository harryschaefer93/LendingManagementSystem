import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.roles import Role, require_role
from app.database import get_db
from app.models.loan import LoanStatus
from app.schemas.audit import AuditLogResponse
from app.schemas.decision import DecisionCreate
from app.schemas.loan import (
    LoanCreate,
    LoanDetailResponse,
    LoanListResponse,
    LoanResponse,
    LoanUpdate,
)
from app.services import audit_service, loan_service

router = APIRouter(prefix="/loans", tags=["loans"])


@router.get("", response_model=LoanListResponse)
async def list_loans(
    status: LoanStatus | None = Query(None),
    loan_officer_id: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    loans, total = await loan_service.list_loans(
        db,
        status_filter=status,
        loan_officer_id=loan_officer_id,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )
    return LoanListResponse(
        items=[LoanResponse.model_validate(loan) for loan in loans],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("", response_model=LoanResponse, status_code=201)
async def create_loan(
    data: LoanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(Role.officer, Role.admin)),
):
    loan = await loan_service.create_loan(db, data, current_user)
    return LoanResponse.model_validate(loan)


@router.get("/{loan_id}", response_model=LoanDetailResponse)
async def get_loan(
    loan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    loan = await loan_service.get_loan(db, loan_id)
    return LoanDetailResponse.model_validate(loan)


@router.patch("/{loan_id}", response_model=LoanResponse)
async def update_loan(
    loan_id: uuid.UUID,
    data: LoanUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(Role.officer, Role.admin)),
):
    loan = await loan_service.update_loan(db, loan_id, data, current_user)
    return LoanResponse.model_validate(loan)


@router.post("/{loan_id}/submit", response_model=LoanResponse)
async def submit_loan(
    loan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(Role.officer, Role.admin)),
):
    loan = await loan_service.submit_loan(db, loan_id, current_user)
    return LoanResponse.model_validate(loan)


@router.post("/{loan_id}/review", response_model=LoanResponse)
async def start_review(
    loan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(Role.underwriter, Role.admin)),
):
    loan = await loan_service.start_review(db, loan_id, current_user)
    return LoanResponse.model_validate(loan)


@router.post("/{loan_id}/decide", response_model=LoanResponse)
async def decide_loan(
    loan_id: uuid.UUID,
    data: DecisionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(Role.underwriter, Role.admin)),
):
    loan = await loan_service.decide_loan(db, loan_id, data, current_user)
    return LoanResponse.model_validate(loan)


@router.get("/{loan_id}/audit", response_model=list[AuditLogResponse])
async def get_audit_trail(
    loan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Verify loan exists
    await loan_service.get_loan(db, loan_id)
    entries = await audit_service.get_audit_trail(db, loan_id)
    return [AuditLogResponse.model_validate(e) for e in entries]
