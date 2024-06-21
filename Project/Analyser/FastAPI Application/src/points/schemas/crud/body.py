from typing import List

from common.schemas.crud.common import CRUD, create_crud_model
from points.schemas.models import BodyPart
from points.schemas.models.body import SkeletonBase

BodyPartCreate = create_crud_model(
    BodyPart,
    CRUD.CREATE,
    excluded=["skeleton_id", "id"],
)


SkeletonCreate = create_crud_model(
    SkeletonBase,
    CRUD.CREATE,
    parts=(List[BodyPartCreate], ...)
)
