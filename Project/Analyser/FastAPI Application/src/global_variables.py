# APPLICATION GLOBAL VARIABLES
from points.point_variables import PointVariables, variables as point_variables


class GlobalVariables:

    # FastAPI Application
    APP = None
    databases = {}
    point_variables: PointVariables = point_variables


global_variables = GlobalVariables()
