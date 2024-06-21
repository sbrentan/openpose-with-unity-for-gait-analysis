from typing import Callable, Tuple

from fastapi import APIRouter
from starlette.responses import RedirectResponse

from points.database.database import points_database
from points.routers.document.document import router as document_router
from points.routers.skeleton import router as skeleton_router
from global_variables import global_variables

router = APIRouter(
    tags=["points"]
)


async def router_startup(fastapi_app):
    # print("Starting up the points...")
    global_variables.databases["points"] = points_database


async def router_shutdown(fastapi_app):
    # print("Shutting down the points...")
    pass

router_lifespan: Tuple[Callable, Callable] = (router_startup, router_shutdown)


@router.get("/")
async def redirect_to_real_time_analysis():
    return RedirectResponse("skeleton/analysis")


router.include_router(document_router)
router.include_router(skeleton_router)
