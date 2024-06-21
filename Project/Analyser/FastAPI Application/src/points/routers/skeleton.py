from typing import List, Annotated

from fastapi import APIRouter, Depends, Query
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from plotly import graph_objs as go
from starlette.templating import Jinja2Templates

from common.schemas.models.message import SuccessMessage
from points.database.database import get_db, PointsDatabase
from points.schemas.crud.body import SkeletonCreate
from points.schemas.crud.csv_document import GraphType
from points.schemas.models import Skeleton, BodyPart, PartType

router = APIRouter(
    prefix="/skeleton",
    tags=["skeleton"]
)

templates = Jinja2Templates(directory="points/templates")


@router.post("", response_model=SuccessMessage, summary="Create a skeleton",
             description="Create a skeleton using open pose points", response_description="Success if skeleton created")
async def create_skeleton(skeleton: SkeletonCreate, db: PointsDatabase = Depends(get_db)):
    skeletons = await db.skeleton.filter()
    skeleton_id = max([s.id for s in skeletons]) + 1 if len(skeletons) > 0 else 1
    await db.skeleton.create(Skeleton(id=skeleton_id, datetime=skeleton.datetime))

    for part in skeleton.parts:
        await db.body_parts.create(
            BodyPart(
                skeleton_id=skeleton_id,
                part_type=part.part_type,
                x=part.x,
                y=part.y,
            )
        )

    message = SuccessMessage(success=True, message="Skeleton created successfully")
    return message


@router.get("", response_model=List[Skeleton], summary="Get all skeletons",
            description="Get all skeletons from the database", response_description="Success if skeletons retrieved")
async def get_skeletons(db: PointsDatabase = Depends(get_db)):
    result = await db.skeleton.filter()
    return result


@router.get("/{skeleton_id}/parts", response_model=List[BodyPart], summary="Get skeleton parts",
            description="Get all parts of a skeleton", response_description="Success if parts retrieved")
async def get_skeleton_parts(skeleton_id: int, db: PointsDatabase = Depends(get_db)):
    result = await db.skeleton.get(skeleton_id)
    if not result:
        return []
    parts = await db.body_parts.filter(skeleton_id=skeleton_id)
    return parts


@router.get("/analysis", response_class=HTMLResponse, summary="Get skeleton analysis",)
async def get_skeleton_analysis(request: Request, db: PointsDatabase = Depends(get_db)):
    last_point_id = 0
    skeleton_points = await db.skeleton.filter()
    if skeleton_points:
        last_point_id = skeleton_points[-1].id
    return templates.TemplateResponse("skeleton_analysis.html", {"request": request, "last_point_id": last_point_id})


@router.get("/points/graph", tags=["points"], summary="Read all points", description="Read all points",
            response_description="List of all points", response_class=HTMLResponse)
async def read_points_graph(graph_type: GraphType, part_types: Annotated[list[PartType] | None, Query()] = None,
                            db: PointsDatabase = Depends(get_db)) -> HTMLResponse:
    skeleton_list: List[Skeleton] = await db.skeleton.filter()

    figure = go.Figure()

    for part_type in part_types:
        x_axis_values = []
        y_axis_values = []
        for skeleton in skeleton_list:
            skeleton_parts = await db.body_parts.filter(skeleton_id=skeleton.id)
            if not skeleton_parts:
                continue
            if graph_type == GraphType.X_TIME or graph_type == GraphType.Y_TIME:
                x_axis_values.append([skeleton.datetime for part in skeleton_parts if part.part_type == part_type][0])
                if graph_type == GraphType.X_TIME:
                    y_axis_values.append([part.x for part in skeleton_parts if part.part_type == part_type][0])
                else:
                    y_axis_values.append([part.y for part in skeleton_parts if part.part_type == part_type][0])
            elif graph_type == GraphType.X_Y:
                y_axis_values.append([part.x for part in skeleton_parts if part.part_type == part_type][0])
                x_axis_values.append([part.y for part in skeleton_parts if part.part_type == part_type][0])
            elif graph_type == GraphType.Y_X:
                x_axis_values.append([part.x for part in skeleton_parts if part.part_type == part_type][0])
                y_axis_values.append([part.y for part in skeleton_parts if part.part_type == part_type][0])
        figure.add_trace(go.Scatter(x=x_axis_values, y=y_axis_values, mode='lines+markers', name=str(part_type.value)))

    axis_titles = graph_type.value.split("_")
    figure.update_layout(title="Graph " + graph_type.value, xaxis_title=axis_titles[1], yaxis_title=axis_titles[0])

    return HTMLResponse(content=figure.to_html(), status_code=200)


@router.get("/points/new", tags=["points"], summary="Get new points", description="Retrieve new points",
            response_description="List of new points")
async def get_new_points(last_point_id: int, db: PointsDatabase = Depends(get_db)) -> JSONResponse:
    new_skeletons = await db.skeleton.get(last_point_id + 1)
    if not new_skeletons:
        return JSONResponse(content={"skeleton_points": []}, status_code=200)
    new_skeletons = [new_skeletons]
    skeleton_points = [
        {
            **skeleton.model_dump(),
            "parts": [part.model_dump() for part in await db.body_parts.filter(skeleton_id=skeleton.id)]
        }
        for skeleton in new_skeletons
    ]
    if len(skeleton_points) == 1 and not skeleton_points[0]['parts']:
        recent_point_id = db.skeleton.get_last_id()
        return JSONResponse(content={"skeleton_points": [], "last_point": recent_point_id}, status_code=200)

    # SKIPPING DELETION SO THAT I CAN SAVE THE NEW DOCUMENT JUST BY KNOWING THE ID OF THE LAST POINT
    # delete all skeletons and body parts
    # total_body_parts = [skeleton_points[x]["parts"] for x in range(len(skeleton_points))]
    # body_parts_ids = [part.get("id") for part_arr in total_body_parts for part in part_arr]
    # for part_id in body_parts_ids:
    #     await db.body_parts.delete(part_id)

    return JSONResponse(content={"skeleton_points": skeleton_points}, status_code=200)
