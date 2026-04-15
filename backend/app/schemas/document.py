from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.document import DocumentType


class DocumentResponse(BaseModel):
    id: UUID
    loan_id: UUID
    filename: str
    document_type: DocumentType
    blob_url: str
    content_type: str | None = None
    file_size: int | None = None
    uploaded_by: str | None = None
    uploaded_by_name: str | None = None
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    id: UUID
    filename: str
    document_type: DocumentType
    content_type: str | None = None
    file_size: int | None = None
    uploaded_at: datetime

    model_config = {"from_attributes": True}
