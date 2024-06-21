from enum import Enum
from typing import List, Type

from pydantic import create_model, BaseModel


class CRUD(str, Enum):
    CREATE = "Create"
    READ = "Read"
    UPDATE = "Update"
    DELETE = "Delete"


def create_crud_model(model: Type[BaseModel], crud: CRUD, excluded: List = None, **fields):
    if excluded is None:
        excluded = []
    model_class = model.__pydantic_core_schema__["cls"]
    model_fields = {field: field_type.annotation for field, field_type in model.model_fields.items()}
    model_fields = {field: (field_type, ...) for field, field_type in model_fields.items() if field not in excluded}
    crud_model_name = f"{model_class.__name__}{crud.value}"
    return create_model(crud_model_name, **model_fields, **fields)


"""
USAGE EXAMPLE:

class Transaction(BaseModel):
    id: int
    amount: float
    
temp = create_crud_model(
    Transaction,
    CRUD.CREATE,
    excluded=["amount"],
    datetime=(datetime, ...)
)

class TransactionCreate(temp):
    id: str

"""
