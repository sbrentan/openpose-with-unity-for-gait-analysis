from enum import Enum
from typing import List

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class PartType(str, Enum):
    HEAD = "head"
    TRUNK = "trunk"
    RIGHT_HAND = "right_arm"
    LEFT_HAND = "left_arm"
    RIGHT_FOOT = "right_leg"
    LEFT_FOOT = "left_leg"


class BodyPart(SQLModel, table=True):
    id: int = Field(primary_key=True, index=True)
    x: float
    y: float
    part_type: PartType = Field(alias="partType")
    skeleton_id: int = Field(foreign_key="skeleton.id")


class SkeletonBase(BaseModel):
    datetime: float


class Skeleton(SkeletonBase, SQLModel, table=True):
    id: int = Field(primary_key=True, index=True)


class SkeletonParts(SkeletonBase):
    id: int
    parts: List[BodyPart]
