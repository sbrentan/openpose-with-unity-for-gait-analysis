from __future__ import annotations
from functools import wraps
from typing import TypeVar, List, Type, Optional

from pydantic import BaseModel
from sqlmodel import create_engine, Session, select, SQLModel

from common.database.base import BaseCollection, Database

T = TypeVar('T', bound=BaseModel)


class SqliteDatabase(Database):

    session = None
    engine = None

    def __init__(self, database_url: str = None, collections: dict[str, Type[BaseSqliteCollection[T]]] = None):
        super().__init__(collections)
        if database_url:
            self.database_url = database_url
        if not hasattr(self, "database_url") or not self.database_url:
            raise ValueError("Database URL not provided")
        self.engine = create_engine(self.database_url)
        SQLModel.metadata.create_all(self.engine)

    def start(self):
        with Session(self.engine) as session:
            self.session = session

    def commit(self):
        self.session.commit()

    def close(self):
        self.session.close_all()


def validate_instance_sqlmodel(collection_function):
    @wraps(collection_function)
    def wrapper(self, *args, **kwargs):
        if self.session is None:
            raise ValueError("Session not set")
        if self.instance_class is None:
            raise ValueError("Instance class not set")
        if self.sqlmodel_class is None:
            raise ValueError("SQLModel class not set")

        return collection_function(self, *args, **kwargs)

    return wrapper


class BaseSqliteCollection(BaseCollection[T]):

    def __init__(self, database: SqliteDatabase):
        super().__init__(database)
        self.database = database
        self.instance_class: Optional[T] = None
        self.sqlmodel_class: Optional[SQLModel] = None

    @property
    def session(self):
        return self.database.session

    def to_instance(self, sqlmodel_instance):
        if sqlmodel_instance is None:
            return None
        if self.sqlmodel_class == self.instance_class:
            return sqlmodel_instance
        return self.instance_class.model_validate(sqlmodel_instance.model_dump())

    def to_sqlmodel(self, instance):
        if instance is None:
            return None
        if self.sqlmodel_class == self.instance_class:
            return instance
        return self.sqlmodel_class.model_validate(instance.model_dump())

    @validate_instance_sqlmodel
    async def get(self, item_id: int) -> T:
        statement = select(self.sqlmodel_class).where(self.sqlmodel_class.id == item_id)
        result = self.session.exec(statement).first()
        return self.to_instance(result)

    @validate_instance_sqlmodel
    async def filter(self, **kwargs) -> List[T]:
        conditions = [getattr(self.sqlmodel_class, key) == value for key, value in kwargs.items()]
        statement = select(self.sqlmodel_class).where(*conditions)
        result = self.session.exec(statement).all()
        return [self.to_instance(item) for item in result]

    @validate_instance_sqlmodel
    async def create(self, new_item: T, **kwargs) -> T:
        sqlmodel_instance = self.to_sqlmodel(new_item)
        self.session.add(sqlmodel_instance)
        self.session.commit()
        self.session.refresh(sqlmodel_instance)
        return self.to_instance(sqlmodel_instance)

    @validate_instance_sqlmodel
    async def update(self, item: T, **kwargs) -> T:
        sql_item = item
        if sql_item.__class__ != self.sqlmodel_class:
            sql_item = self.session.get(self.sqlmodel_class, item.id)
            for key, value in item.model_dump().items():
                setattr(sql_item, key, value)

        self.session.add(sql_item)
        return item

    @validate_instance_sqlmodel
    async def delete(self, item_id) -> bool:
        statement = select(self.sqlmodel_class).where(self.sqlmodel_class.id == item_id)
        result = self.session.exec(statement).first()
        if result is None:
            return False
        self.session.delete(result)
        return True
