from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from starlette.responses import HTMLResponse

from points.database.database import get_db, PointsDatabase
from points.schemas.crud.csv_document import GraphType
from points.schemas.models import PartType
from plotly import graph_objs as go

from points.schemas.models.body import SkeletonParts

router = APIRouter()


templates = Jinja2Templates(directory="points/templates")


@router.get("/points", tags=["points"], summary="Read all points",
            description="Read all points", response_description="List of all points",
            response_model=list[SkeletonParts])
async def read_points(document_id: int, db: PointsDatabase = Depends(get_db)) -> list[SkeletonParts]:
    document = await db.document.get(document_id)
    skeleton_list = document.skeletons
    return skeleton_list


@router.get("/points/analysis", tags=["analysis"], response_class=HTMLResponse)
async def get_points_analysis(request: Request, document_id: int, db: PointsDatabase = Depends(get_db)) -> HTMLResponse:
    document = await db.document.get(document_id)
    return templates.TemplateResponse("points_analysis.html", {"request": request, "document": document})


@router.get("/points/graph", tags=["points"], summary="Read all points", description="Read all points",
            response_description="List of all points", response_class=HTMLResponse)
async def read_points_graph(document_id: int, graph_type: GraphType, part_types: Annotated[list[PartType] | None, Query()] = None,
                            db: PointsDatabase = Depends(get_db)) -> HTMLResponse:
    document = await db.document.get(document_id)
    skeleton_list = document.skeletons

    figure = go.Figure()

    a = 0
    for part_type in part_types:
        x_axis_values = []
        y_axis_values = []
        for skeleton in skeleton_list:
            if graph_type == GraphType.X_TIME or graph_type == GraphType.Y_TIME:
                x_axis_values.append([skeleton.datetime for part in skeleton.parts if part.part_type == part_type][0])
                if graph_type == GraphType.X_TIME:
                    y_axis_values.append([part.x for part in skeleton.parts if part.part_type == part_type][0])
                else:
                    y_axis_values.append([part.y for part in skeleton.parts if part.part_type == part_type][0])
            elif graph_type == GraphType.X_Y:
                y_axis_values.append([part.x for part in skeleton.parts if part.part_type == part_type][0])
                x_axis_values.append([part.y for part in skeleton.parts if part.part_type == part_type][0])
            elif graph_type == GraphType.Y_X:
                x_axis_values.append([part.x for part in skeleton.parts if part.part_type == part_type][0])
                y_axis_values.append([part.y for part in skeleton.parts if part.part_type == part_type][0])
        x_axis_values.pop(0)
        y_axis_values.pop(0)
        figure.add_trace(go.Scatter(x=x_axis_values, y=y_axis_values, mode='lines+markers', name=str(part_type.value)))

    title = GraphType.get_graph_title(graph_type.value)
    x_name, y_name = GraphType.get_axis_names(graph_type.value)
    figure.update_layout(title=title, xaxis_title=x_name, yaxis_title=y_name)

    return HTMLResponse(content=figure.to_html(), status_code=200)
