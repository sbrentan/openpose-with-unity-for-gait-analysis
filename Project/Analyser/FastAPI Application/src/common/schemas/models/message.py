from typing import Optional

from pydantic import BaseModel


class SuccessMessage(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None
