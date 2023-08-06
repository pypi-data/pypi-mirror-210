import json
import logging

# Utilities.
from dls_utilpack.callsign import callsign
from dls_utilpack.require import require

# Dataface interface.
from dls_servbase_api.datafaces.datafaces import Datafaces

# Base class for cookie things.
from dls_servbase_lib.cookies.base import Base as CookieBase

logger = logging.getLogger(__name__)

thing_type = "dls_servbase_lib.cookies.dataface"


class Dataface(CookieBase):
    """ """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification=None, predefined_uuid=None):
        CookieBase.__init__(
            self, thing_type, specification, predefined_uuid=predefined_uuid
        )

        self.__type_specific_tbd = require(
            f"{callsign(self)} specification", self.specification(), "type_specific_tbd"
        )

        dataface_specification = require(
            f"{callsign(self)} specification root",
            self.__type_specific_tbd,
            "dataface_specification",
        )

        self.__dataface = Datafaces().build_object(dataface_specification)

    # ----------------------------------------------------------------------------------------
    async def load_from_persist(self):
        """
        Load cookie contents from persistent storage.
        """

        if self.__dataface is None:
            raise RuntimeError("disallowed attempt to reload from persist")

        record = await self.__dataface.get_cookie(self.uuid())

        if record is None:
            self.set_contents({})
        else:
            self.set_contents(json.loads(record["contents"]))

    # ----------------------------------------------------------------------------------------
    async def save_to_persist(self):
        if self.has_contents():
            contents = self.get_contents()
        else:
            contents = {}

        record = await self.__dataface.get_cookie(self.uuid())
        # logger.debug(describe("[COOKOFF] saving cookie record", record))

        if record is None:
            # logger.debug(
            #     f"[COOKOFF] creating cookie record for {self.uuid()} {contents}"
            # )
            record = {
                "uuid": self.uuid(),
                "name": self.traits()["cookie_name"],
                "contents": json.dumps(contents),
            }
            await self.__dataface.set_cookie(record)
        else:
            record = {"uuid": self.uuid(), "contents": json.dumps(contents)}
            # logger.debug(
            #     f"[COOKOFF] updating cookie record for {self.uuid()} {contents}"
            # )
            await self.__dataface.update_cookie(record)

    # ----------------------------------------------------------------------------------------
    async def release(self):
        """
        Release cookie and free its connections and other resources.
        """

        logger.debug(
            f"[RELCOOK] releasing client to cookie dataface {str(self.__dataface)}"
        )
        if self.__dataface is not None:
            await self.__dataface.close_client_session()
            self.__dataface = None
