from enum import Enum

from pydantic import BaseModel, Field

from points.schemas.models import PartType


class CSVDocumentCreate(BaseModel):
    name: str
    csv_file: str = Field(alias="csvFile")


class GraphType(Enum):
    X_Y: str = "x_y"
    Y_X: str = "y_x"
    X_TIME: str = "x_time"
    Y_TIME: str = "y_time"

    @classmethod
    def get_graph_title(cls, graph_type: str) -> str:
        if graph_type == cls.X_Y.value:
            return "Graph X vs Y"
        elif graph_type == cls.Y_X.value:
            return "Graph Y vs X"
        elif graph_type == cls.X_TIME.value:
            return "Graph X vs Time"
        elif graph_type == cls.Y_TIME.value:
            return "Graph Y vs Time"
        return "Unknown"

    @classmethod
    def get_axis_names(cls, graph_type: str) -> tuple[str, str]:
        if graph_type == cls.X_Y.value:
            return "Y", "X"
        elif graph_type == cls.Y_X.value:
            return "X", "Y"
        elif graph_type == cls.X_TIME.value:
            return "Time", "X"
        elif graph_type == cls.Y_TIME.value:
            return "Time", "Y"
        return "Unknown", "Unknown"
