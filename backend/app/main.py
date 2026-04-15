from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.dependencies import get_current_user
from app.config import settings
from app.routers import documents, health, loans
from fastapi import Depends

app = FastAPI(
    title="Lending Management System",
    description="POC for internal loan lifecycle management",
    version="1.0.0",
)

# CORS
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, prefix="/api")
app.include_router(loans.router, prefix="/api")
app.include_router(documents.router, prefix="/api")


@app.get("/api/me", tags=["auth"])
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user
