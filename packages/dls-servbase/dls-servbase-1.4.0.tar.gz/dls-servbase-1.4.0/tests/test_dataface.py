import logging

from dls_servbase_api.databases.constants import CookieFieldnames, Tablenames
from dls_servbase_api.datafaces.context import Context as ClientContext
from dls_servbase_api.datafaces.datafaces import dls_servbase_datafaces_get_default
from dls_servbase_lib.datafaces.context import Context as ServerContext

# Base class for the tester.
from tests.base_context_tester import BaseContextTester

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestDatafaceSqlite:
    """
    Test that we can do a basic database operation through the service.
    """

    def test(self, constants, logging_setup, output_directory):
        """ """

        configuration_file = "tests/configurations/sqlite.yaml"
        DatafaceTester().main(constants, configuration_file, output_directory)


# ----------------------------------------------------------------------------------------
class TestDatafaceMysql:
    """
    Test that we can do a basic database operation through the service.
    """

    def test(self, constants, logging_setup, output_directory):
        """ """

        configuration_file = "tests/configurations/mysql.yaml"
        DatafaceTester().main(constants, configuration_file, output_directory)


# ----------------------------------------------------------------------------------------
class DatafaceTester(BaseContextTester):
    """
    Class to test the dataface.
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

                # ----------------------------------------------------------------
                # Now try a direct update.
                record = {
                    CookieFieldnames.CONTENTS: "{'b': 'f1111'}",
                }

                subs = ["f0"]
                result = await dataface.update(
                    Tablenames.COOKIES,
                    record,
                    f"{CookieFieldnames.UUID} = ?",
                    subs=subs,
                    why="test update",
                )

                assert result["count"] == 1
                records = await dataface.query(all_sql)

                assert len(records) == 1
                assert records[0][CookieFieldnames.UUID] == "f0"
                assert records[0][CookieFieldnames.CONTENTS] == "{'b': 'f1111'}"

                # ----------------------------------------------------------------
                # Now try a high level API update.
                record = {
                    CookieFieldnames.UUID: "f0",
                    CookieFieldnames.CONTENTS: "{'c': 'f2222'}",
                }

                result = await dataface.update_cookie(
                    record,
                )

                assert result["count"] == 1
                records = await dataface.query(all_sql)

                assert len(records) == 1
                assert records[0][CookieFieldnames.UUID] == "f0"
                assert records[0][CookieFieldnames.CONTENTS] == "{'c': 'f2222'}"
