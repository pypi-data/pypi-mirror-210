import logging

# Base class for table definitions.
from dls_normsql.table_definition import TableDefinition

from dls_servbase_api.databases.constants import CookieFieldnames, Tablenames

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class CookiesTableDefinition(TableDefinition):
    # ----------------------------------------------------------------------------------------
    def __init__(self):
        TableDefinition.__init__(self, Tablenames.COOKIES)

        # All cookies have a unique uuid field.
        self.fields[CookieFieldnames.UUID] = {
            "type": "TEXT PRIMARY KEY",
            "index": True,
        }

        self.fields[CookieFieldnames.CREATED_ON] = {"type": "TEXT", "index": True}
        self.fields[CookieFieldnames.NAME] = {"type": "TEXT", "index": True}
        self.fields[CookieFieldnames.CONTENTS] = {"type": "TEXT", "index": False}
