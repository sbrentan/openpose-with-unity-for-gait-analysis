from enum import Enum
from typing import TypeVar, List, Type

from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from common.database.base import BaseCollection, Database

T = TypeVar('T', bound=BaseModel)


Base = declarative_base()


class PostgresDatabase(Database):

    session_local = None
    session = None
    engine = None

    def __init__(self, database_url: str, collections: dict[str, Type[BaseCollection[T]]]):
        super().__init__(collections)
        self.engine = create_engine(database_url)
        self.session_local = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def start(self):
        with self.session_local() as session:
            self.session = session

    def close(self):
        self.session_local.close_all()


class BasePostgresCollection(BaseCollection[T]):

    def __init__(self, database: PostgresDatabase):
        super().__init__(database)
        self.session = database.session
        self.collection = None
        self.instance_class = None
        self.postgres_class = None

    def to_pydantic(self, item, model):
        if item is None:
            return None
        if getattr(model, '__origin__', None) is list:
            return [self.to_pydantic(i, model.__args__[0]) for i in item]

        return self.instance_class(**item.__dict__)

    def to_postgres(self, item: BaseModel, postgres_model):
        return postgres_model(**{k: (str(v) if isinstance(v, Enum) else v) for k, v in item.model_dump().items()})

    async def get(self, item_id: str) -> T:
        item = self.session.query(self.postgres_class).filter(self.postgres_class.id == item_id).first()
        return self.to_pydantic(item, self.instance_class)

    async def filter(self, **kwargs) -> List[T]:
        items = self.session.query(self.postgres_class).all()
        return self.to_pydantic(items, List[self.instance_class])

    async def create(self, new_item: T, **kwargs) -> T:
        new_item_postgres = self.to_postgres(new_item, self.postgres_class)
        self.session.add(new_item_postgres)
        self.session.commit()
        self.session.refresh(new_item_postgres)
        return self.to_pydantic(new_item_postgres, self.instance_class)

    async def update(self, item: T, **kwargs) -> T:
        self.session.query(self.postgres_class).filter(self.postgres_class.id == item.id).update(item.model_dump())
        self.session.commit()
        return item

    async def delete(self, item_id) -> bool:
        self.session.query(self.postgres_class).filter(self.postgres_class.id == item_id).delete()
        self.session.commit()
        return True
