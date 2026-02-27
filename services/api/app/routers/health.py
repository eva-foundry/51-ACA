# EVA-STORY: ACA-11-001
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    version: str = "0.1.0"
    environment: str = "unknown"


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    from app.settings import get_settings
    s = get_settings()
    return HealthResponse(status="ok", environment=s.ACA_ENVIRONMENT)
