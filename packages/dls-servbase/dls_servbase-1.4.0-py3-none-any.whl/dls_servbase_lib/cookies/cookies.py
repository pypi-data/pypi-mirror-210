# Use standard logging in this module.
import logging

# Class managing list of things.
from dls_utilpack.things import Things

# Exceptions.
from dls_servbase_api.exceptions import NotFound

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------------------
__default_cookie = None


def cookies_set_default(cookie):
    global __default_cookie
    __default_cookie = cookie


def cookies_get_default():
    global __default_cookie
    if __default_cookie is None:
        raise RuntimeError("cookies_get_default instance is None")
    return __default_cookie


# -----------------------------------------------------------------------------------------


class Cookies(Things):
    """
    List of available cookies.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, name=None):
        Things.__init__(self, name)

    # ----------------------------------------------------------------------------------------
    def build_object(self, specification, predefined_uuid=None):
        """"""

        cookie_class = self.lookup_class(specification["type"])

        try:
            cookie_object = cookie_class(specification, predefined_uuid=predefined_uuid)
        except Exception as exception:
            raise RuntimeError(
                "unable to build cookie object for type %s" % (cookie_class)
            ) from exception

        return cookie_object

    # ----------------------------------------------------------------------------------------
    def lookup_class(self, class_type):
        """"""

        if class_type == "dls_servbase_lib.cookies.dataface":
            from dls_servbase_lib.cookies.dataface import Dataface

            return Dataface

        raise NotFound("unable to get cookie class for type %s" % (class_type))
