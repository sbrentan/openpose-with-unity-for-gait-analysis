from common.database.sqlite import BaseSqliteCollection, SqliteDatabase
from points.schemas.models import CSVDocument


class CSVDocumentCollection(BaseSqliteCollection[CSVDocument]):

    def __init__(self, database: SqliteDatabase):
        super().__init__(database)
        self.instance_class = CSVDocument
        self.sqlmodel_class = CSVDocument
