import uuid
from datetime import datetime, timedelta, timezone

from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from fastapi import HTTPException, UploadFile, status

from app.config import settings

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _get_blob_service_client() -> BlobServiceClient:
    if not settings.AZURE_STORAGE_CONNECTION_STRING:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Azure Blob Storage is not configured. Set AZURE_STORAGE_CONNECTION_STRING.",
        )
    return BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)


async def upload_document(
    file: UploadFile,
    loan_id: uuid.UUID,
) -> tuple[str, int]:
    """Upload a file to Azure Blob Storage. Returns (blob_url, file_size)."""
    # Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{file.content_type}' not allowed. Allowed: PDF, JPEG, PNG.",
        )

    # Read and validate size
    content = await file.read()
    file_size = len(content)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size {file_size} bytes exceeds maximum of {MAX_FILE_SIZE} bytes (10MB).",
        )

    blob_name = f"{loan_id}/{uuid.uuid4()}/{file.filename}"

    try:
        blob_service = _get_blob_service_client()
        container_client = blob_service.get_container_client(settings.AZURE_STORAGE_CONTAINER_NAME)

        # Create container if it doesn't exist
        try:
            container_client.get_container_properties()
        except Exception:
            container_client.create_container()

        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(content, content_settings={"content_type": file.content_type})

        return blob_client.url, file_size
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}",
        )


def generate_download_url(blob_url: str) -> str:
    """Generate a SAS URL for downloading a blob with 15-minute expiry."""
    if not settings.AZURE_STORAGE_CONNECTION_STRING:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Azure Blob Storage is not configured.",
        )

    try:
        blob_service = _get_blob_service_client()
        # Parse account name and key from connection string
        account_name = blob_service.account_name

        # Extract the blob path from the URL
        # URL format: https://<account>.blob.core.windows.net/<container>/<path>
        url_parts = blob_url.split(f"{settings.AZURE_STORAGE_CONTAINER_NAME}/", 1)
        if len(url_parts) != 2:
            raise ValueError("Cannot parse blob URL")
        blob_name = url_parts[1]

        # Get account key from connection string
        conn_parts = dict(
            part.split("=", 1)
            for part in settings.AZURE_STORAGE_CONNECTION_STRING.split(";")
            if "=" in part
        )
        account_key = conn_parts.get("AccountKey", "")

        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=settings.AZURE_STORAGE_CONTAINER_NAME,
            blob_name=blob_name,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(minutes=15),
        )

        return f"{blob_url}?{sas_token}"
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate download URL: {str(e)}",
        )
