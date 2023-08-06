"""
Station Class
"""
# Standard library modules
import warnings
import logging

# Non-standard modules
from obspy.core.inventory.station import Station as obspy_Station

from obspy.core.inventory.util import (Site, Comment)
from obspy.core.utcdatetime import UTCDateTime
# from obspy.taup.seismic_phase import self_tokenizer

# obsinfo modules
from .processing import Processing
from obsinfo.instrumentation import (Instrumentation, Location)
from .operator_class import Operator
from obsinfo.obsMetadata.obsmetadata import (ObsMetadata)

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class Station(object):
    """
    Station. Equivalent to obspy/StationXML Station

    Methods convert info files to an instance of this class and convert the
    object to an `obspy` object.

    Attributes:
        label:
        site (str):
        start_date (str with date format): station start date
        end_date (str with date format): station end date
        location_code (str):
        restricted_status (str): status of station
        locations (list of :class:`.Location`)
        location (:class:`.Location`): default location code
            of channels, corresònding to `location_code`
        instrumentation (:class:`.Instrumentation` or list of
            :class:`.Instrumentation`):
        processing (list of objects of :class:`.Processing`) : attributes
            for clock correction processing
        comments (list of str):
        extras (list of str):
        obspy_station (:class:`obspy.core.inventory.station.Station`):
            Equivalent obspy object
    """

    def __init__(self, label, attributes_dict, station_only=False,
                 stations_operator=None):
        """
        Constructor

        Args:
            attributes_dict: (dict or :class:`.ObsMetadata`): dictionary
                from station or network info file with YAML or JSON attributes
            station_only (boolean): Creates object with no instrumentation
            stations_operator (:class:`.Operator`): default station operator
        Raises:
            TypeError
        """
        if not attributes_dict:
            msg = 'No station attributes'
            warnings.warn(msg)
            logger.error(msg)
            raise TypeError(msg)

        self.label = label
        self.site = attributes_dict.get("site", None)

        start_date = ObsMetadata.validate_date(
            attributes_dict.get("start_date", None))
        self.start_date = UTCDateTime(start_date) if start_date else None
        end_date = ObsMetadata.validate_date(attributes_dict.get("end_date",
                                                                 None))
        self.end_date = UTCDateTime(end_date) if end_date else None
        self.location_code = attributes_dict.get("location_code", None)
        self.serial_number = attributes_dict.get("serial_number", None)
        self.restricted_status = attributes_dict.get("restricted_status", None)
        op = attributes_dict.get("operator", None)
        if op is None:
            self.operator = stations_operator
        else:
            self.operator = Operator(op)

        self.locations = {c: Location(v) for c, v in
                          attributes_dict.get('locations', None).items()}
        self.location = Location.get_location_from_code(
            self.locations, self.location_code, "station", self.label)

        instr_list = attributes_dict.get('instrumentations', None)
        if instr_list and isinstance(instr_list, list):
            channel_modifs = attributes_dict.get('channel_modifications', {})
            self.instrumentation = [Instrumentation(inst, self.locations,
                                                    start_date, end_date,
                                                    channel_modifs,
                                                    self.serial_number)
                                    for inst in instr_list]
        else:
            instr_dict = attributes_dict.get('instrumentation', None)
            channel_modifs = attributes_dict.get('channel_modifications', {})
            # print()
            # print(f'Station: {attributes_dict=}, {channel_modifs=}')

            if instr_dict:
                self.instrumentation = Instrumentation(
                    instr_dict, self.locations, start_date, end_date,
                    channel_modifs, self.serial_number)
            elif station_only:
                # Create StationXML file with no instrumentation w/o
                # raising an exception
                self.instrumentation = None
            else:
                msg = f'No instrumentation in station "{self.site}"'
                # warnings.warn(msg)
                logger.error(msg)
                raise ValueError(msg)

        # Locations, start_date and end_date are used to creat obspy Channel
        self.comments = attributes_dict.get("commnents", [])
        self.extras = [str(k) + ": " + str(v)
                       for k, v in (attributes_dict.get('extras', {})).items()]
        self.processing = Processing(attributes_dict.get('processing', None))

        self.convert_comments_in_obspy()
        self.obspy_station = self.to_obspy()

    def __repr__(self):
        s = f'\nStation(Label={self.label}, Site={self.site}, '
        s += f'Start Date={self.start_date}, End Date={self.end_date}, '
        s += f'Location Code={self.location_code}, '
        s += f'{len(self.locations)} Locations, '
        if self.processing:
            s += f'processing-steps: {self.processing.processing_list}'
        # if not self.restricted_stations == "unknown":
        #    s += f', {self.restricted_status}'
        s += ')'
        return s

    def to_obspy(self):
        """
        Convert station object to obspy object

        Returns:
            (:class:`obspy.core.inventory.station.Station`):
                  corresponding obspy Station object
        """
        start_date = UTCDateTime(self.start_date) if self.start_date else None
        end_date = UTCDateTime(self.end_date) if self.end_date else None
        site = Site(name=self.site, description=None, town=None, county=None,
                    region=None, country=None)
        comments = [Comment(s) for s in self.comments]

        if self.instrumentation:
            channels_number = len(self.instrumentation.channels)
            chnl_list = [ch.obspy_channel
                         for ch in self.instrumentation.channels]
            equip_list = [self.instrumentation.equipment]
        else:
            channels_number = 0
            chnl_list = []
            equip_list = []

        if self.operator is not None:
            operators = [self.operator.to_obspy()]
        else:
            operators = None

        obspy_station = obspy_Station(
            code=self.label,
            latitude=self.location.obspy_latitude,
            longitude=self.location.obspy_longitude,
            elevation=self.location.obspy_elevation,
            channels=chnl_list,
            site=site,
            vault=self.location.vault,
            geology=self.location.geology,
            equipments=equip_list,
            operators=operators,
            creation_date=start_date,
            termination_date=end_date,
            total_number_of_channels=channels_number,
            selected_number_of_channels=channels_number,
            description=None,
            comments=comments,
            start_date=start_date,
            end_date=end_date,
            restricted_status=self.restricted_status,
            alternate_code=None,
            historical_code=None,
            data_availability=None,
            identifiers=None,
            water_level=None,
            source_id=None)
        return obspy_station

    def convert_comments_in_obspy(self):
        """
        Convert info file notes and extras to XML comments
        """

        if self.extras:
            self.comments.append('EXTRA ATTRIBUTES (for documentation only):')
            self.comments = self.comments + self.extras
        if self.processing.processing_list:
            self.comments.append(self.processing.processing_list)
