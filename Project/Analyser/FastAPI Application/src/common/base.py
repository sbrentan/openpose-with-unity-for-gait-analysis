from fastapi import APIRouter

from common.routers.healthz import router as healthz_router

router = APIRouter(
    tags=["common"],
)

router.include_router(healthz_router, prefix="/healthz")
