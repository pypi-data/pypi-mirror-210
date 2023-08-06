"""
Network :class:

"""
# Standard library modules
import warnings
import logging

# Non-standard modules
from obspy.core.inventory.network import Network as obspy_Network
# from obspy.core.inventory.util import (Person, Comment, PhoneNumber)
from obspy.core.inventory.util import (Comment)
from obspy.core.utcdatetime import UTCDateTime

# obsinfo modules
from .station import (Station)
from .operator_class import Operator

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class Network(object):
    """
    Network obsinfo: Equivalent to obspy/StationXML Network

    Attributes:
         campaign_ref (str)
         fdsn_code (str)
         fdsn_name (str)
         start_date (str with date format)
         end_date (str with date format)
         description  (str)
         restricted_status (str)
         operator (object of :class:`.Operator`)
         stations (list of objects of :class:`.Station`)
         comments (list of str)
         extras (list of str)
         obspy_network (:class~`obspy.core.inventory.network.Network):
           obspy equivalent of this class
    """

    def __init__(self, attributes_dict=None, station_only=False):
        """
        Constructor

        Args:
            attributes_dict (dict or :class:`.ObsMetadata`): dictionary from
                network info file
            station_only (bool): Instructs class Station to create object
                with no instrumentation
        Raises:
            (TypeError): if attributes_dict is empty
        """
        if not attributes_dict:
            msg = 'No network attributes'
            logger.error(msg)
            raise TypeError(msg)

        self.campaign_ref = attributes_dict.get("campaign_ref_name", None)
        network_info = attributes_dict.get("network_info", None)

        if network_info:
            self.fdsn_code = network_info.get("code", None)
            self.fdsn_name = network_info.get("name", None)
            self.start_date = network_info.get("start_date", 0)
            self.end_date = network_info.get("end_date", 0)
            self.description = network_info.get("description", None)

        self.restricted_status = attributes_dict.get("restricted_status", None)
        self.operator = Operator(attributes_dict.get("operator", None))
        st_op = attributes_dict.get("stations_operator", None)
        if st_op is None:
            stations_operator = self.operator
        else:
            stations_operator = Operator(st_op)

        stations = attributes_dict.get("stations", None)
        self.stations = [Station(k, v, station_only, stations_operator)
                         for k, v in stations.items()]

        self.comments = attributes_dict.get("comments", [])
        self.extras = [str(k) + ": " + str(v)
                       for k, v in (attributes_dict.get('extras', {})).items()]
        self.convert_notes_and_extras_to_obspy()

        self.obspy_network = self.to_obspy()

    def __repr__(self):
        s = f'Network(Campaign: {self.campaign_ref}, '
        s += f'FDSN Code: {self.fdsn_code}, FDSN Name: {self.fdsn_code}, '
        s += f'Start date: {self.start_date}, End date: {self.end_date}, '
        s += 'Description: {self.description}, '
        s += f'{len(self.stations)} stations)'
        return s

    def to_obspy(self):
        """
         Convert network object to obspy object

         Returns:
            (:class:~obspy.core.inventory.network.Network): corresponding
                obspy Network
        """
        # This should be done in the Operator class, not here
        if self.operator:
            operator = self.operator.to_obspy()
        else:
            operator = None

        stations_number = len(self.stations)
        start_date = UTCDateTime(self.start_date) if self.start_date else None
        end_date = UTCDateTime(self.end_date) if self.end_date else None
        comments = [Comment(s) for s in self.comments]

        self.obspy_network = obspy_Network(
            code=self.fdsn_code,
            stations=[st.obspy_station for st in self.stations],
            total_number_of_stations=stations_number,
            selected_number_of_stations=stations_number,
            description=self.fdsn_name + " - " + self.description,
            comments=comments,
            start_date=start_date,
            end_date=end_date,
            restricted_status=self.restricted_status,
            alternate_code=None,
            historical_code=None,
            data_availability=None,
            identifiers=None,
            operators=[operator],
            source_id=None)
#         for st in self.stations:  # complete stations
#             st.operators = [operator]
        return self.obspy_network

    def convert_notes_and_extras_to_obspy(self):
        """
        Convert info file notes and extras to XML comments
        """
        if self.extras:
            self.comments.append('EXTRA ATTRIBUTES (for documentation only):')
            if isinstance(self.extras, list):
                self.comments.extend(self.extras)
            else:
                self.comments.append(self.extras)
