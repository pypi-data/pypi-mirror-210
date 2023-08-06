"""
InstrumentComponent class and subclasses Sensor, Preamplifier, Datalogger.
Equipment class
"""
# Standard library modules
import warnings
import logging

# Non-standard modules
from obspy.core.inventory.util import Equipment as obspy_Equipment
from obspy.core.utcdatetime import UTCDateTime

# obsinfo
from obsinfo.obsMetadata.obsmetadata import (ObsMetadata)

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class Equipment(obspy_Equipment):
    """
    Equipment.

    Equivalent to :class: obspy.core.inventory.util.Equipment

    Attributes:
        type (str):
        channel_modif (str):
        selected_config (str):
        description (str):
        manufacturer (str):
        model (str):
        vendor (str):
        serial_number (str):
        installation_date (str in date format):
        removal_date (str in date format):
        calibration_dates (str in date format):
        resource_id (str):
        obspy_equipment (class `obspy.core.inventory.equipmentEquipment`)`
    """

    def __init__(self, attributes_dict, channel_modif={}, selected_config={}):
        """
        Constructor

        Args:
            attributes_dict (dict or :class:`ObsMetadata`): attributes of
                component, hopefully including configuration_default
            channel_modif (dict or :class:`ObsMetadata`): channel modifications
                inherited from station
            selected_config (sdict or :class:`ObsMetadata`): configuration dict
                selected at instrument_component level

        """
        self.type = attributes_dict.get_configured_element(
            'type', channel_modif, selected_config, None)
        self.description = attributes_dict.get_configured_element(
            'description', channel_modif, selected_config, None)
        self.manufacturer = attributes_dict.get_configured_element(
            'manufacturer', channel_modif, selected_config, None)
        self.model = attributes_dict.get_configured_element(
            'model', channel_modif, selected_config, None)
        self.vendor = attributes_dict.get_configured_element(
            'vendor', channel_modif, selected_config, None)
        self.serial_number = attributes_dict.get_configured_element(
            'serial_number', channel_modif, selected_config, None)
        self.installation_date = ObsMetadata.validate_date(
            attributes_dict.get_configured_element('installation_date',
                                                   channel_modif,
                                                   selected_config,
                                                   None))
        self.removal_date = ObsMetadata.validate_date(
            attributes_dict.get_configured_element('removal_date',
                                                   channel_modif,
                                                   selected_config,
                                                   None))
        calibration_dates = ObsMetadata.validate_dates(
            attributes_dict.get_configured_element('calibration_dates',
                                                   channel_modif,
                                                   selected_config,
                                                   []))

        self.calibration_dates = calibration_dates
        self.resource_id = None

        equip = self.to_obspy()
        self.obspy_equipment = equip[0] if isinstance(equip, tuple) else equip

    def __repr__(self):
        s = 'Equipment('
        if self.type:
            s += f', Type={self.type}'
        if self.description:
            s += f', Description={self.description}'
        if self.manufacturer:
            s += f', Manufacturer={self.manufacturer}'
        if self.model:
            s += f', Model={self.model}'
        if self.vendor:
            s += f', Vendor={self.vendor}'
        if self.serial_number:
            s += f', Serial Number={self.serial_number}'
        if self.installation_date:
            s += f', Installation Date={self.installation_date}'
        if self.removal_date:
            s += f', Removal Date={self.removal_date}'
        if self.calibration_dates:
            s += f', Calibration Date={self.calibration_dates}'
        s += ')'
        return s

    def to_obspy(self):
        """
        Convert an equipment (including the equipment description in
        components) to its obspy object

        Returns:
            (:class:`obspy.core.invertory.util.Equipment`)
        """
        resource_id = None

        installation_date = UTCDateTime(self.installation_date) \
            if self.installation_date else None
        removal_date = UTCDateTime(self.removal_date) \
            if self.removal_date else None

        if isinstance(self.calibration_dates, list) \
                and len(self.calibration_dates) > 0:
            calib_dates = [UTCDateTime(dt)
                           for dt in self.calibration_dates]
        else:
            calib_dates = []

        equip = obspy_Equipment(self.type, self.description, self.manufacturer,
                                self.vendor, self.model, self.serial_number,
                                installation_date, removal_date,
                                calib_dates, resource_id)

        return equip
