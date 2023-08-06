import logging

from dls_normsql.constants import ClassTypes
from dls_normsql.databases import Databases

from dls_servbase_api.databases.constants import CookieFieldnames, Tablenames
from dls_servbase_api.databases.database_definition import DatabaseDefinition
from tests.base_tester import BaseTester2

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestDatabaseSqlite:
    def test(self, constants, logging_setup, output_directory):
        """
        Tests the sqlite implementation of the Database interface.

        This does not use a service.
        """

        database_specification = {
            "type": ClassTypes.AIOSQLITE,
            "filename": "%s/dls_servbase_pytest.sqlite" % (output_directory),
        }

        # Test direct SQL access to the database.
        DatabaseTester().main(
            constants,
            database_specification,
            output_directory,
        )


# ----------------------------------------------------------------------------------------
class TestDatabaseMysql:
    def test(self, constants, logging_setup, output_directory):
        """
        Tests the sqlite implementation of the Database interface.

        This does not use a service.
        """

        database_specification = {
            "type": ClassTypes.AIOMYSQL,
            "type_specific_tbd": {
                "database_name": "dls_servbase_pytest",
                "host": "$MYSQL_HOST",
                "port": "$MYSQL_PORT",
                "username": "root",
                "password": "root",
            },
        }

        # Test direct SQL access to the database.
        DatabaseTester().main(
            constants,
            database_specification,
            output_directory,
        )


# ----------------------------------------------------------------------------------------
class DatabaseTester(BaseTester2):
    """
    Test direct SQL access to the database.
    """

    async def _main_coroutine(
        self, constants, database_specification, output_directory
    ):
        """ """

        databases = Databases()
        database = databases.build_object(
            database_specification,
            DatabaseDefinition(),
        )

        try:
            # Connect to database.
            await database.connect(should_drop_database=True)

            # Write one record.
            await database.insert(
                Tablenames.COOKIES,
                [
                    {
                        CookieFieldnames.UUID: "f0",
                        CookieFieldnames.CONTENTS: "{'a': 'f000'}",
                    }
                ],
            )
            all_sql = f"SELECT * FROM {Tablenames.COOKIES}"
            records = await database.query(all_sql)
            assert len(records) == 1

            # Bulk insert more records.
            insertable_records = [
                ["f1", "{'a': 'f111'}"],
                ["f2", "{'a': 'f111'}"],
                ["f3", "{'a': 'f111'}"],
                ["f4", "{'a': 'f111'}"],
            ]
            await database.execute(
                f"INSERT INTO {Tablenames.COOKIES}"
                f" ({CookieFieldnames.UUID}, {CookieFieldnames.CONTENTS})"
                " VALUES (?, ?)",
                insertable_records,
            )

            all_sql = f"SELECT * FROM {Tablenames.COOKIES}"
            records = await database.query(all_sql)
            assert len(records) == 5

        finally:
            # Connect from the database... necessary to allow asyncio loop to exit.
            await database.disconnect()
