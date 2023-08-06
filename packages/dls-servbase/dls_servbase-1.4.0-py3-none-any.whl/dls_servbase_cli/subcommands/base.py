import logging
import os
import tempfile

from dls_multiconf_lib.multiconfs import Multiconfs, multiconfs_set_default

# Utilities.
from dls_utilpack.visit import get_visit_year

logger = logging.getLogger(__name__)


class Base:
    """
    Base class for femtocheck subcommands.  Handles details like configuration.
    """

    def __init__(self, args):
        self._args = args

        self.__temporary_directory = None

    # ----------------------------------------------------------------------------------------
    def get_multiconf(self):

        dls_servbase_multiconf = Multiconfs().build_object_from_environment()

        # For convenience, make a temporary directory for this test.
        self.__temporary_directory = tempfile.TemporaryDirectory()

        # Make the temporary directory available to the multiconf.
        dls_servbase_multiconf.substitute(
            {"temporary_directory": self.__temporary_directory.name}
        )

        substitutions = {
            "APPS": "/dls_sw/apps",
            "CWD": os.getcwd(),
            "HOME": os.environ.get("HOME", "HOME"),
            # Provide the PYTHONPATH at the time of service start
            # to the (potentially remote) process where the dls_servbase_task.run is called.
            "PYTHONPATH": os.environ.get("PYTHONPATH", "PYTHONPATH"),
        }

        if hasattr(self._args, "visit") and self._args.visit != "VISIT":
            BEAMLINE = os.environ.get("BEAMLINE")
            if BEAMLINE is None:
                raise RuntimeError("BEAMLINE environment variable is not defined")
            year = get_visit_year(BEAMLINE, self._args.visit)
            substitutions["BEAMLINE"] = BEAMLINE
            substitutions["VISIT"] = self._args.visit
            substitutions["YEAR"] = year

        dls_servbase_multiconf.substitute(substitutions)

        # Set this as the default multiconf so it is available everywhere.
        multiconfs_set_default(dls_servbase_multiconf)

        return dls_servbase_multiconf
