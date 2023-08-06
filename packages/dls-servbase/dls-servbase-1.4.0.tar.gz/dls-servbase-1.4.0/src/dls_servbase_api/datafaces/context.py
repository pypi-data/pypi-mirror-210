import logging

# Things created in the context.
from dls_servbase_api.datafaces.datafaces import (
    Datafaces,
    dls_servbase_datafaces_set_default,
)

logger = logging.getLogger(__name__)


class Context:
    """
    Client context for a dls_servbase_dataface object.
    On entering, it creates the object according to the specification (a dict).
    On exiting, it closes client connection.

    The aenter and aexit methods are exposed for use by an enclosing context.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification):
        self.__specification = specification
        self.__dls_servbase_dataface = None

    # ----------------------------------------------------------------------------------------
    async def __aenter__(self):
        """ """

        await self.aenter()

    # ----------------------------------------------------------------------------------------
    async def __aexit__(self, type, value, traceback):
        """ """

        await self.aexit()

    # ----------------------------------------------------------------------------------------
    async def aenter(self):
        """ """

        # Build the object according to the specification.
        self.__dls_servbase_dataface = Datafaces().build_object(self.__specification)

        # If there is more than one dataface, the last one defined will be the default.
        dls_servbase_datafaces_set_default(self.__dls_servbase_dataface)

    # ----------------------------------------------------------------------------------------
    async def aexit(self):
        """ """

        if self.__dls_servbase_dataface is not None:
            await self.__dls_servbase_dataface.close_client_session()

            # Clear the global variable.  Important between pytests.
            dls_servbase_datafaces_set_default(None)
