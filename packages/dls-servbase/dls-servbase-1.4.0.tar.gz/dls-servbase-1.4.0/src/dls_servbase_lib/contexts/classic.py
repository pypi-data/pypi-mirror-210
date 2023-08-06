import logging

from dls_utilpack.callsign import callsign

# Utilities.
from dls_utilpack.explain import explain

# Base class which maps flask requests to methods.
from dls_servbase_lib.contexts.base import Base

# Contexts.
from dls_servbase_lib.datafaces.context import Context as DatafaceContext
from dls_servbase_lib.guis.context import Context as GuiContext

logger = logging.getLogger(__name__)


thing_type = "dls_servbase_lib.dls_servbase_contexts.classic"


class Classic(Base):
    """
    Object representing an event dls_servbase_dataface connection.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification):
        Base.__init__(self, thing_type, specification)

        self.__dataface = None
        self.__collector = None
        self.__gui = None

    # ----------------------------------------------------------------------------------------
    async def __dead_or_alive(self, server, dead, alive):

        if server is not None:
            # A server was defined for this context?
            if await server.is_process_started():
                if await server.is_process_alive():
                    alive.append(server)
                else:
                    dead.append(server)

    # ----------------------------------------------------------------------------------------
    async def __dead_or_alive_all(self):
        """
        Return two lists, one for dead and one for alive processes.
        TODO: Parallelize context process alive/dead checking.
        """

        dead = []
        alive = []

        await self.__dead_or_alive(self.__dataface, dead, alive)
        await self.__dead_or_alive(self.__collector, dead, alive)
        await self.__dead_or_alive(self.__gui, dead, alive)

        return dead, alive

    # ----------------------------------------------------------------------------------------
    async def is_any_process_alive(self):
        """
        Check all configured processes, return if any alive.
        """
        dead, alive = await self.__dead_or_alive_all()

        logger.debug(f"{len(dead)} processes are dead, {len(alive)} are alive")

        return len(alive) > 0

    # ----------------------------------------------------------------------------------------
    async def is_any_process_dead(self):
        """
        Check all configured processes, return if any alive.
        """
        dead, alive = await self.__dead_or_alive_all()

        return len(dead) > 0

    # ----------------------------------------------------------------------------------------
    async def __aenter__(self):
        """ """
        logger.debug(f"entering {callsign(self)} context")

        try:

            try:
                specification = self.specification().get(
                    "dls_servbase_dataface_specification"
                )
                if specification is not None:
                    logger.debug(f"at entering position {callsign(self)} DATAFACE")
                    self.__dataface = DatafaceContext(specification)
                    await self.__dataface.aenter()
            except Exception as exception:
                raise RuntimeError(
                    explain(exception, f"creating {callsign(self)} dataface context")
                )

            try:
                specification = self.specification().get(
                    "dls_servbase_gui_specification"
                )
                if specification is not None:
                    logger.debug(f"at entering position {callsign(self)} GUI")
                    self.__gui = GuiContext(specification)
                    await self.__gui.aenter()
            except Exception as exception:
                raise RuntimeError(
                    explain(exception, f"creating {callsign(self)} gui context")
                )

        except Exception as exception:
            await self.aexit()
            raise RuntimeError(explain(exception, f"entering {callsign(self)} context"))

        logger.debug(f"entered {callsign(self)} context")

    # ----------------------------------------------------------------------------------------
    async def __aexit__(self, type, value, traceback):
        """ """

        await self.aexit()

    # ----------------------------------------------------------------------------------------
    async def aexit(self):
        """ """

        logger.debug(f"exiting {callsign(self)} context")

        if self.__gui is not None:
            logger.debug(f"at exiting position {callsign(self)} GUI")
            try:
                await self.__gui.aexit()
            except Exception as exception:
                logger.error(
                    explain(exception, f"exiting {callsign(self.__gui)} context"),
                    exc_info=exception,
                )
            self.__gui = None

        if self.__dataface is not None:
            logger.debug(f"at exiting position {callsign(self)} DATAFACE")
            try:
                await self.__dataface.aexit()
            except Exception as exception:
                logger.error(
                    explain(exception, f"exiting {callsign(self.__dataface)} context"),
                    exc_info=exception,
                )
            self.__dataface = None

        logger.debug(f"exited {callsign(self)} context")
