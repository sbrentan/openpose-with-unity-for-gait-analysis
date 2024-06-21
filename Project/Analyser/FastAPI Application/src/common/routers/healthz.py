from fastapi import APIRouter

from common.schemas.models.healthz import HealthStatus

router = APIRouter()


@router.get("", response_model=HealthStatus)
async def health_status():
    return HealthStatus(status="ok")
