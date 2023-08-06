import logging

from dls_servbase_api.databases.constants import CookieFieldnames, Tablenames

# Base class for all aiosqlite database objects.
from dls_servbase_api.databases.table_definitions import CookiesTableDefinition

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class DatabaseDefinition:
    """
    Class which defines the database tables and revision migration path.
    Used in concert with the normsql class.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self):
        """
        Construct object.  Do not connect to database.
        """

        self.LATEST_REVISION = 2

    # ----------------------------------------------------------------------------------------
    async def apply_revision(self, database, revision):
        if revision == 2:
            await database.execute(
                f"ALTER TABLE {Tablenames.COOKIES} ADD COLUMN {CookieFieldnames.NAME} TEXT",
                why=f"revision 2: add {Tablenames.COOKIES} {CookieFieldnames.NAME} column",
            )
            await database.execute(
                "CREATE INDEX %s_%s ON %s(%s)"
                % (
                    Tablenames.COOKIES,
                    CookieFieldnames.NAME,
                    Tablenames.COOKIES,
                    CookieFieldnames.NAME,
                )
            )

    # ----------------------------------------------------------------------------------------
    async def add_table_definitions(self, database):
        """
        Make all the table definitions.
        """

        # Table schemas in our database.
        database.add_table_definition(CookiesTableDefinition())
