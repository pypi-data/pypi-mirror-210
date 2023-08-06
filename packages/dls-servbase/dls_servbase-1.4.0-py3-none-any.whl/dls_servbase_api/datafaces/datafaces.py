# Use standard logging in this module.
import logging

# Class managing list of things.
from dls_utilpack.things import Things

# Exceptions.
from dls_servbase_api.exceptions import NotFound

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------------------
__default_dls_servbase_dataface = None


def dls_servbase_datafaces_set_default(dls_servbase_dataface):
    global __default_dls_servbase_dataface
    __default_dls_servbase_dataface = dls_servbase_dataface


def dls_servbase_datafaces_get_default():
    global __default_dls_servbase_dataface
    if __default_dls_servbase_dataface is None:
        raise RuntimeError("dls_servbase_datafaces_get_default instance is None")
    return __default_dls_servbase_dataface


# -----------------------------------------------------------------------------------------


class Datafaces(Things):
    """
    List of available dls_servbase_datafaces.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, name=None):
        Things.__init__(self, name)

    # ----------------------------------------------------------------------------------------
    def build_object(self, specification):
        """"""

        dls_servbase_dataface_class = self.lookup_class(specification["type"])

        try:
            dls_servbase_dataface_object = dls_servbase_dataface_class(specification)
        except Exception as exception:
            raise RuntimeError(
                "unable to build dls_servbase_dataface object for type %s"
                % (dls_servbase_dataface_class)
            ) from exception

        return dls_servbase_dataface_object

    # ----------------------------------------------------------------------------------------
    def lookup_class(self, class_type):
        """"""

        if class_type == "dls_servbase_lib.datafaces.aiohttp":
            from dls_servbase_api.datafaces.aiohttp import Aiohttp

            return Aiohttp

        raise NotFound(
            "unable to get dls_servbase_dataface class for type %s" % (class_type)
        )
