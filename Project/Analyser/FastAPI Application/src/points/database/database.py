from common.database.sqlite import SqliteDatabase
from points.database.collections.body_part import BodyPartCollection
from points.database.collections.document import CSVDocumentCollection
from points.database.collections.skeleton import SkeletonCollection
from points.settings import DATABASE_URL


class PointsDatabase(SqliteDatabase):
    document: CSVDocumentCollection
    skeleton: SkeletonCollection
    body_parts: BodyPartCollection
    database_url = DATABASE_URL


points_database = PointsDatabase()


async def get_db():
    try:
        points_database.start()
        yield points_database
        points_database.commit()
    finally:
        # Close the database connection when the request is done
        points_database.close()
