import logging

from dls_servbase_api.databases.constants import CookieFieldnames, Tablenames
from dls_servbase_api.datafaces.context import Context as ClientContext
from dls_servbase_api.datafaces.datafaces import dls_servbase_datafaces_get_default
from dls_servbase_lib.datafaces.context import Context as ServerContext

# Base class for the tester.
from tests.base_context_tester import BaseContextTester

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestDatafaceTakeoverSqlite:
    def test(self, constants, logging_setup, output_directory):
        """ """

        configuration_file = "tests/configurations/sqlite.yaml"
        DatafaceTakeoverTester().main(constants, configuration_file, output_directory)


# ----------------------------------------------------------------------------------------
class TestDatafaceTakeoverMysql:
    """
    Test that we can do a basic database operation through the service.
    """

    def test(self, constants, logging_setup, output_directory):
        """ """

        configuration_file = "tests/configurations/mysql.yaml"
        DatafaceTakeoverTester().main(constants, configuration_file, output_directory)


# ----------------------------------------------------------------------------------------
class DatafaceTakeoverTester(BaseContextTester):
    """
    Class to test that a second instance of the dataface will cause the first one to shut down.
    """

    async def _main_coroutine(self, constants, output_directory):
        """ """

        dls_servbase_multiconf = self.get_multiconf()

        context_configuration = await dls_servbase_multiconf.load()

        servbase_specification = context_configuration[
            "dls_servbase_dataface_specification"
        ]

        dls_servbase_client_context = ClientContext(servbase_specification)

        dls_servbase_server_context = ServerContext(servbase_specification)

        async with dls_servbase_client_context:
            async with dls_servbase_server_context:
                dataface = dls_servbase_datafaces_get_default()

                # Write one record.
                await dataface.insert(
                    Tablenames.COOKIES,
                    [
                        {
                            CookieFieldnames.UUID: "f0",
                            CookieFieldnames.CONTENTS: "{'a': 'f000'}",
                        }
                    ],
                )
                all_sql = f"SELECT * FROM {Tablenames.COOKIES}"
                records = await dataface.query(all_sql)

                assert len(records) == 1
                assert records[0][CookieFieldnames.UUID] == "f0"
                assert records[0][CookieFieldnames.CONTENTS] == "{'a': 'f000'}"

            # ----------------------------------------------------------------------------
            # Make a new dataface context with the same specification, except don't drop.
            servbase_specification["type_specific_tbd"][
                "actual_dataface_specification"
            ]["should_drop_database"] = False
            dls_servbase_server_context = ServerContext(servbase_specification)
            # Activate the new dataface which should send shutdown to the old process.
            async with dls_servbase_server_context:
                # Check the final insert made it to the database.
                records = await dataface.query(all_sql)
                assert len(records) == 1
                assert records[0][CookieFieldnames.UUID] == "f0"
                assert records[0][CookieFieldnames.CONTENTS] == "{'a': 'f000'}"

                # Update the cookie record.
                subs = []
                subs.append("f0")
                await dataface.update(
                    Tablenames.COOKIES,
                    {CookieFieldnames.CONTENTS: "{'a': 'f001'}"},
                    f"{CookieFieldnames.UUID} = ?",
                    subs=subs,
                    why="update database revision",
                )

            # ----------------------------------------------------------------------------
            # Make a new dataface context with the same specification, again without dropping.
            dls_servbase_server_context = ServerContext(servbase_specification)
            # Activate the new dataface which should send shutdown to the old process.
            async with dls_servbase_server_context:
                # Check the final update made it to the database.
                records = await dataface.query(all_sql)
                assert len(records) == 1
                assert records[0][CookieFieldnames.UUID] == "f0"
                assert records[0][CookieFieldnames.CONTENTS] == "{'a': 'f001'}"
