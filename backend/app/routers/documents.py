import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.document import Document, DocumentType
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.services import audit_service, document_service, loan_service

router = APIRouter(prefix="/loans/{loan_id}/documents", tags=["documents"])


@router.post("", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    loan_id: uuid.UUID,
    document_type: DocumentType = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Verify loan exists
    await loan_service.get_loan(db, loan_id)

    blob_url, file_size = await document_service.upload_document(file, loan_id)

    doc = Document(
        loan_id=loan_id,
        filename=file.filename or "untitled",
        document_type=document_type,
        blob_url=blob_url,
        content_type=file.content_type,
        file_size=file_size,
        uploaded_by=current_user["id"],
        uploaded_by_name=current_user["name"],
    )
    db.add(doc)
    await db.flush()

    await audit_service.write_audit_log(
        db,
        loan_id=loan_id,
        action="document_uploaded",
        actor_id=current_user["id"],
        actor_name=current_user["name"],
        details=f"Document uploaded: {file.filename} (type={document_type.value}, size={file_size})",
    )

    return DocumentUploadResponse.model_validate(doc)


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    loan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Verify loan exists
    await loan_service.get_loan(db, loan_id)

    result = await db.execute(
        select(Document).where(Document.loan_id == loan_id).order_by(Document.uploaded_at.desc())
    )
    return [DocumentResponse.model_validate(d) for d in result.scalars().all()]


@router.get("/{document_id}/download")
async def download_document(
    loan_id: uuid.UUID,
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Verify loan exists
    await loan_service.get_loan(db, loan_id)

    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.loan_id == loan_id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    download_url = document_service.generate_download_url(doc.blob_url)
    return {"download_url": download_url, "filename": doc.filename, "content_type": doc.content_type}
