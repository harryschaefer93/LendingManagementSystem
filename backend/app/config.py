from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://lmsadmin:password@localhost:5432/lms"
    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_STORAGE_CONTAINER_NAME: str = "documents"
    CORS_ORIGINS: str = "http://localhost:3000"
    AUTH_MODE: str = "mock"  # "mock" or "entra"
    ENTRA_TENANT_ID: str = ""
    ENTRA_CLIENT_ID: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
