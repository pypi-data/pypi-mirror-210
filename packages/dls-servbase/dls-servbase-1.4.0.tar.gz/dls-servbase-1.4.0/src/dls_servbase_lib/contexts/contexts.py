# Use standard logging in this module.
import logging

import yaml

# Class managing list of things.
from dls_utilpack.things import Things

# Exceptions.
from dls_servbase_api.exceptions import NotFound

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------------------


class Contexts(Things):
    """
    Context loader.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, name=None):
        Things.__init__(self, name)

    # ----------------------------------------------------------------------------------------
    def build_object(self, specification):
        """"""

        if not isinstance(specification, dict):
            with open(specification, "r") as yaml_stream:
                specification = yaml.safe_load(yaml_stream)

        dls_servbase_context_class = self.lookup_class(specification["type"])

        try:
            dls_servbase_context_object = dls_servbase_context_class(specification)
        except Exception as exception:
            raise RuntimeError(
                "unable to build dls_servbase_context object for type %s"
                % (dls_servbase_context_class)
            ) from exception

        return dls_servbase_context_object

    # ----------------------------------------------------------------------------------------
    def lookup_class(self, class_type):
        """"""

        if class_type == "dls_servbase_lib.dls_servbase_contexts.classic":
            from dls_servbase_lib.contexts.classic import Classic

            return Classic

        raise NotFound(
            "unable to get dls_servbase_context class for type %s" % (class_type)
        )
