from sqlalchemy import select

from common.database.sqlite import BaseSqliteCollection, SqliteDatabase
from points.schemas.models import Skeleton


class SkeletonCollection(BaseSqliteCollection[Skeleton]):

    def __init__(self, database: SqliteDatabase):
        super().__init__(database)
        self.instance_class = Skeleton
        self.sqlmodel_class = Skeleton

    def get_last_id(self):
        statement = select(self.sqlmodel_class).order_by(self.sqlmodel_class.id.desc()).limit(1)
        result = self.session.exec(statement).first()
        return result[0].id if result else 0
