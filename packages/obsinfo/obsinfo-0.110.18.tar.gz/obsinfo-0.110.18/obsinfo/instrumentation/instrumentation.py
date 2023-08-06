"""
Instrumentation class
"""
# Standard library modules
import warnings
import logging

# Non-standard modules

# obsinfo modules
from obsinfo.obsMetadata.obsmetadata import (ObsMetadata)
from .instrument_component import Equipment
from .channel import Channel
# from .operator_class import Operator

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class Instrumentation(object):
    """
    One or more Instruments. Part of an obspy/StationXML Station

    Methods convert info files to an instance of this class. No equivalent
    obspy/StationXML class

    A more detailed description the class and its attributes is found in XXX

    Attributes:
        equipment (:class:`Equipment`):
        channels (list): list of channels (:class:`Channel`)
    """
    def __init__(self, attributes_dict_or_list, locations,
                 start_date, end_date, channel_modifs={},
                 serial_number=None):
        """
        Constructor

        attributes_dict may contain a configuration_selection for the
        instrumentation and the corresponding configs for the components:
        datalogger, preamplifier and sensor

        Args:
            attributes_dict_or_list (dict/ObsMetadata or list of same):
                instrumentation(s) attributes
            locations (list):  of :class:`Locations`
            start_date (str): start date
            end_date (str): end date
            channel_modifs (dict or :class:`ObsMetadata`):
                modification of attributes per channel specified in stations
            serial_number (str): instrumentation (OBS) serial number.
                Configures nothing for now

        locations, start_date and end_date are inherited from the
        corresponding attributes in a station to fill out StationXML fields.
        It is assumed an instrumentation default location,
        start date and end_date are the same as its station's.
        """
        # Syntax checking - Check whether
        if not attributes_dict_or_list:
            msg = 'No instrumentation attributes'
            warnings.warn(msg)
            logger.error(msg)
            raise TypeError(msg)
        elif isinstance(attributes_dict_or_list, list):
            # Easy mistake of including a dash in the yaml file
            msg = 'Instrumentation should be unique, not a list. Removing '\
                  'list embedding.'
            warnings.warn(msg)
            logger.warning(msg)

            if len(attributes_dict_or_list) > 0:
                attributes_dict = attributes_dict_or_list[0]
            else:
                msg = 'No instrumentation attributes'
                warnings.warn(msg)
                logger.error(msg)
                raise TypeError(msg)
        else:
            attributes_dict = attributes_dict_or_list

        # self.operator = Operator(attributes_dict.get('operator', None))
        self.equipment = Equipment(
            ObsMetadata(attributes_dict.get('equipment', None)), {}, {})
        if serial_number is not None:
            self.equipment.serial_number = serial_number
        self.equipment.obspy_equipment = self.equipment.to_obspy()

        das_channels = attributes_dict.get('channels', {})
        channel_default = das_channels.get('default', {})
        if channel_default:
            del das_channels['default']

        # v here is the attributes_dict of each das_channel
        self.channels = [Channel(label, attributes, locations,
                                 start_date, end_date,
                                 self.equipment.obspy_equipment,
                                 channel_default, channel_modifs)
                         for label, attributes in das_channels.items()]

    def __repr__(self):
        s = f'\n\nInstrumentation({len(self.channels)-1} channels)'
        return s
