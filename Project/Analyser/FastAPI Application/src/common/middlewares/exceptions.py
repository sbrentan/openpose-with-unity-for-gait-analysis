import traceback

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from common.schemas.models.exceptions import RequestException


class ExceptionResponse(BaseModel):
    detail: str


class ExceptionMiddleware(BaseHTTPMiddleware):

    def __init__(self, app, some_attribute: str):
        super().__init__(app)
        self.some_attribute = some_attribute

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
        except RequestException as e:
            traceback.print_exc()
            exception_response = ExceptionResponse(detail=str(e))
            return JSONResponse(content=jsonable_encoder(exception_response), status_code=400)

        return response
