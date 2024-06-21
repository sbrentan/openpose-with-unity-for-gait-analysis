from common.database.sqlite import BaseSqliteCollection
from points.schemas.models import BodyPart


class BodyPartCollection(BaseSqliteCollection[BodyPart]):

    def __init__(self, database):
        super().__init__(database)
        self.instance_class = BodyPart
        self.sqlmodel_class = BodyPart
