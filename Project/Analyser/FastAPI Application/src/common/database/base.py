from __future__ import annotations
from abc import abstractmethod, ABC
from typing import Type

from pydantic import BaseModel
from motor import motor_asyncio
from typing import TypeVar, Generic, List

T = TypeVar('T', bound=BaseModel)


class BaseCollection(ABC, Generic[T]):

    def __init__(self, database: Database):
        self.collection = None
        self.database = database
        self.instance_class = None

    @abstractmethod
    async def get(self, item_id: str) -> T:
        raise NotImplementedError

    @abstractmethod
    async def filter(self, **kwargs) -> List[T]:
        raise NotImplementedError

    @abstractmethod
    async def create(self, new_item: T, **kwargs) -> T:
        raise NotImplementedError

    @abstractmethod
    async def update(self, item: T, **kwargs) -> T:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, item_id) -> bool:
        raise NotImplementedError


class Database(ABC):

    def __init__(self, collections: dict[str, Type[BaseCollection]]):
        self.database = None
        self._instantiate_collections(collections)

    def _instantiate_collections(self, collections: dict[str, Type[BaseCollection]] = None):
        if collections:
            self.collections = collections
        elif not hasattr(self, "collections"):
            self.collections = {}
            for annotation, value in self.__annotations__.items():
                if issubclass(value, BaseCollection):
                    self.collections[annotation] = value

        self.collections = {
            collection_name: collection.__call__(self) for collection_name, collection in self.collections.items()
        }

        for collection_name, collection in self.collections.items():
            setattr(self, collection_name, self.collections[collection_name])

    def get_collection(self, collection_name):
        return self.collections[collection_name]

    def __getitem__(self, item):
        return self.get_collection(item)

    @abstractmethod
    def start(self):
        raise NotImplementedError

    @abstractmethod
    def close(self):
        raise NotImplementedError


class MongoDatabase(Database):

    database = None
    client = None

    def __init__(self, database_url: str, collections: dict[str, Type[BaseCollection]]):
        super().__init__(collections)
        self.database_url = database_url
        self.collections = collections

    def start(self):
        self.client = motor_asyncio.AsyncIOMotorClient(self.database_url)
        self.database = self.client.melius

    def close(self):
        self.database.client.close()
