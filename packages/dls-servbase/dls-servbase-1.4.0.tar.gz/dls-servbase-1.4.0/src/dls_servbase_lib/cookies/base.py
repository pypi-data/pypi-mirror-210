import logging

# Utilities.
from dls_utilpack.callsign import callsign

# Base class for generic things.
from dls_utilpack.thing import Thing

logger = logging.getLogger(__name__)


class Base(Thing):
    """ """

    # ----------------------------------------------------------------------------------------
    def __init__(self, thing_type, specification=None, predefined_uuid=None):
        Thing.__init__(self, thing_type, specification, predefined_uuid=predefined_uuid)

        self.__contents = None
        self.__is_dirty = False

    # -----------------------------------------------------------------------------
    def set_dirty(self, dirty=True):
        self.__is_dirty = dirty

    def is_dirty(self):
        return self.__is_dirty

    def set_contents(self, contents):
        self.__contents = contents

    def get_contents(self):
        if self.__contents is None:
            raise RuntimeError(f"{callsign(self)} contents has not been set")
        return self.__contents

    def has_contents(self):
        return self.__contents is not None
