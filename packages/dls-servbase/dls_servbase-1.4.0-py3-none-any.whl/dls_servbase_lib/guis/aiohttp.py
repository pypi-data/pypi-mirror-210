import logging
import multiprocessing
import threading

# Utilities.
from dls_utilpack.callsign import callsign
from dls_utilpack.require import require

# Basic things.
from dls_utilpack.thing import Thing

# Base class for an aiohttp server.
from dls_servbase_lib.base_aiohttp import BaseAiohttp

# Gui protocolj things (must agree with javascript).
from dls_servbase_lib.guis.constants import Commands, Cookies, Keywords

logger = logging.getLogger(__name__)

thing_type = "dls_servbase_lib.dls_servbase_guis.aiohttp"


# ------------------------------------------------------------------------------------------
class Aiohttp(Thing, BaseAiohttp):
    """
    Object implementing remote procedure calls for dls_servbase_gui methods.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification=None):
        Thing.__init__(self, thing_type, specification)
        BaseAiohttp.__init__(
            self,
            specification["type_specific_tbd"]["aiohttp_specification"],
            calling_file=__file__,
        )

    # ----------------------------------------------------------------------------------------
    def callsign(self):
        """"""
        return "%s %s" % ("Gui.Aiohttp", BaseAiohttp.callsign(self))

    # ----------------------------------------------------------------------------------------
    def activate_process(self):
        """"""

        try:
            multiprocessing.current_process().name = "gui"

            self.activate_process_base()

        except Exception as exception:
            logger.exception(
                f"unable to start {callsign(self)} process", exc_info=exception
            )

    # ----------------------------------------------------------------------------------------
    def activate_thread(self, loop):
        """
        Called from inside a newly created thread.
        """

        try:
            threading.current_thread().name = "gui"

            self.activate_thread_base(loop)

        except Exception as exception:
            logger.exception(
                f"unable to start {callsign(self)} thread", exc_info=exception
            )

    # ----------------------------------------------------------------------------------------
    async def activate_coro(self):
        """"""
        try:
            # No special routes, we will use protocolj dispathcing only
            route_tuples = []

            # Start the actual coro to listen for incoming http requests.
            await self.activate_coro_base(route_tuples)

        except Exception:
            raise RuntimeError(f"unable to start {callsign(self)} server coro")

    # ----------------------------------------------------------------------------------------
    async def direct_shutdown(self):
        """"""

        # Let the base class stop the server looping.
        await self.base_direct_shutdown()

    # ----------------------------------------------------------------------------------------
    async def dispatch(self, request_dict, opaque):
        """"""

        command = require("request json", request_dict, Keywords.COMMAND)

        if command == Commands.LOAD_TABS:
            return await self._load_tabs(opaque, request_dict)

        if command == Commands.SELECT_TAB:
            return await self._select_tab(opaque, request_dict)

        else:
            raise RuntimeError("invalid command %s" % (command))

    # ----------------------------------------------------------------------------------------
    async def _load_tabs(self, opaque, request_dict):

        tab_id = await self.get_cookie_content(
            opaque,
            Cookies.TABS_MANAGER,
            Keywords.TAB_ID,
            xfrom="guis.Aiohttp_load_tabs",
        )
        logger.debug(f"[GUITABS] tab_id from cookie content is {tab_id}")

        # Reply with tabs.
        response = {Keywords.TAB_ID: tab_id}

        return response

    # ----------------------------------------------------------------------------------------
    async def _select_tab(self, opaque, request_dict):
        tab_id = require("request json", request_dict, Keywords.TAB_ID)

        logger.debug(f"[GUITABS] tab_id in request is {tab_id}")

        # Put the tab_id into the cookie.
        self.set_cookie_content(opaque, Cookies.TABS_MANAGER, Keywords.TAB_ID, tab_id)

        response = {}

        return response
