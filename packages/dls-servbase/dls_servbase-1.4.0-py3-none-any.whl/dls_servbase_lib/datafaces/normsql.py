import logging

# Database manager.
from dls_normsql.databases import Databases

# Base class for generic things.
from dls_utilpack.thing import Thing

from dls_servbase_api.databases.constants import Tablenames
from dls_servbase_api.databases.database_definition import DatabaseDefinition

logger = logging.getLogger(__name__)

thing_type = "dls_servbase_lib.datafaces.normsql"


class Normsql(Thing):
    """ """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification=None):
        Thing.__init__(self, thing_type, specification)

        # For testing, caller might want to drop the database on connection.
        self.__should_drop_database = specification.get("should_drop_database")

        self.__database = None

    # ----------------------------------------------------------------------------------------
    async def start(self):
        # Connect to the database to create the schemas if they don't exist already.
        await self.establish_database_connection()

    # ----------------------------------------------------------------------------------------
    async def disconnect(self):
        if self.__database is not None:
            await self.__database.disconnect()
            self.__database = None

    # ----------------------------------------------------------------------------------------
    async def establish_database_connection(self):

        if self.__database is None:
            self.__database = Databases().build_object(
                self.specification()["database"],
                DatabaseDefinition(),
            )

            # For testing, caller might want to drop the database on connection.
            await self.__database.connect(
                should_drop_database=self.__should_drop_database
            )

    # ----------------------------------------------------------------------------------------
    async def reinstance(self):
        """"""
        if self.__database is None:
            return

        self.__database = self.__database.reinstance()

    # ----------------------------------------------------------------------------------------
    async def set_cookie(self, record):
        """ """
        await self.establish_database_connection()

        await self.__database.insert(Tablenames.COOKIES, [record])

    # ----------------------------------------------------------------------------------------
    async def get_cookie(self, cookie_uuid):
        """
        Get single cookie from its uuid.
        Returns database record format.
        """
        await self.establish_database_connection()

        sql = "SELECT * FROM cookies WHERE uuid = '%s'" % (cookie_uuid)

        records = await self.__database.query(sql, why="[COOKSEL]")

        if len(records) == 0:
            return None

        return records[0]

    # ----------------------------------------------------------------------------------------
    async def update_cookie(self, row):
        """"""
        await self.establish_database_connection()

        count = await self.__database.update(
            Tablenames.COOKIES, row, "uuid = '%s'" % (row["uuid"]), why="[COOKSEL]"
        )

        return {"count": count}

    # ----------------------------------------------------------------------------------------
    async def backup(self):
        """"""
        await self.establish_database_connection()

        return await self.__database.backup()

    # ----------------------------------------------------------------------------------------
    async def restore(self, nth):
        """"""
        await self.establish_database_connection()

        return await self.__database.restore(nth)

    # ----------------------------------------------------------------------------------------
    async def query(self, sql, subs=None, why=None):
        """"""
        await self.establish_database_connection()

        records = await self.__database.query(sql, subs=subs, why=why)

        return records

    # ----------------------------------------------------------------------------------------
    async def execute(self, sql, subs=None, why=None):
        """"""
        await self.establish_database_connection()

        return await self.__database.execute(sql, subs=subs, why=why)

    # ----------------------------------------------------------------------------------------
    async def insert(self, table_name, records, why=None):
        """"""
        await self.establish_database_connection()

        if why is None:
            why = f"insert {len(records)} {table_name} records"

        await self.__database.insert(table_name, records, why=why)

    # ----------------------------------------------------------------------------------------
    async def update(self, table_name, record, where, subs=None, why=None):
        """"""
        await self.establish_database_connection()

        if why is None:
            why = f"update {table_name} record"

        # This returns the count of records changed by the update.
        return {
            "count": await self.__database.update(
                table_name, record, where, subs=subs, why=why
            )
        }

    # ----------------------------------------------------------------------------------------
    async def report_health(self):
        """"""

        report = {}

        report["alive"] = True

        return report
