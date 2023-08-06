"""
Processing Class, holds list of data processing steps
"""

# Standard library modules
import warnings
import logging
import json

# Non-standard modules

# obsinfo modules

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class Processing(object):
    """
    No equivalent class in obspy/StationXML

    Saves a list of Processing steps as strings
    For now, just stores the list. Will be converted to StationXML comments

    Attributes:
        processing_list (list): list of processing steps with attributes,
            either linear_drift or leapsecond

    """

    def __init__(self, attributes):
        """
        Constructor

        Args:
        attributes (list): list of processing steps (linear_drift or
            leapsecond) with attributes
        """

        self.processing_list = []

        if not attributes:
            return

        # make it a list for standard processing if user forgot the dash
        if not isinstance(attributes, list):
            attributes = [attributes]

        # Wayne added self.attributes to allow makescript_LC2SDS
        self.attributes = attributes

        for attr in attributes:
            self.processing_list.append(json.dumps(attr))

    def __repr__(self):
        s = f'Processing({self.processing_list})'
        return s
