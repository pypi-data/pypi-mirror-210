"""
Channel, Instrument and Operator classes
"""
# Standard library modules
import warnings
import logging

# Non-standard modules
from obspy.core.inventory.channel import Channel as obspy_Channel
from obspy.core.inventory.util import (Comment)

# obsinfo modules
from obsinfo.obsMetadata.obsmetadata import (ObsMetadata)
from .location import Location
from .orientation import Orientation
from .instrument import Instrument

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class Channel(object):
    """
    Corresponds to StationXML/obspy Channel plus channel code

    Attributes:
        das_channel (:class:`ObsMetadata`): represents a channel with defaults
            incorporated
        orientation_code (str): orientation code for this channel (part of
            its ID)
        location_code (str): location code for this channel (part of its ID)
        location (:class:`Location`): represents location corresponding to
            location_code
        start_date (str): inherited from Station
        end_date (str): inherited from Station
        instrument (:class:`Instrument`): a sensor, a datalogger and an
            optional preamplifier
        orientation (:class:`Location`):
        comments (str)
        extras (str)
        obspy_channel (:class:`obspy.core.inventory.channel.Channel`): The
            obspy equivalent  of this object
    """

    def __init__(self, label, attributes, locations,
                 start_date, end_date, equipment, channel_default={},
                 channel_modifs={}):
        """
        Constructor

        Args:
            label (str): label to identify channel. Different from the
                channel id code and only used in the information file.
            attributes (dict/ObsMetadata object or list of
                dicts//ObsMetadata objects): channel attributes
            locations (list of :class:`Location`):
            start_date: (str): using date format
            end_date: (str): using date format
            channel_default (dict or :class:`ObsMetadata`): default attributes
                to complement attributes specified in attributes
            channel_modifs (dict or :class:`ObsMetadata`): modification of
                attributes per channel specified in stations
        """
        if label == "default":
            return

        if not attributes:
            msg = 'No channel attributes'
            warnings.warn(msg)
            logger.error(msg)
            raise TypeError(msg)

        # Complete das channel fields with default fields. This will create a
        # complete channel
        self.das_channel = ObsMetadata(self.complete_channel(attributes,
                                                             channel_default))
        # Location and orientation code should not be changed, so no channel
        # modifications.  Default is always 00
        self.location_code = self.das_channel.get('location_code', "00")

        # This is just the one-letter string code, Although the attribute
        # is redundant, it si needed before calling class Orientation init
        # at the bottom of this method
        self.orientation_code = self.get_orientation_code(
            attributes.get('orientation_code', None))

        self.location = Location.get_location_from_code(
            locations, self.location_code, "channel", self.channel_id_code)

        self.start_date = start_date
        self.end_date = end_date

        selected_channel_modifs = self.get_selected_channel_modifs(
            self.channel_id_code, channel_modifs)

        self.instrument = Instrument(self.das_channel, selected_channel_modifs)

        # This is the complete dictionary under key orientation code.
        # If present, azimuth and dip can be changed in channel modifications
        orientation_dict = self.das_channel.get('orientation_code', None)
        if isinstance(orientation_dict, str):
            # If just a string, convert to dict to simplify code
            orientation_dict = {orientation_dict: {}}

        orientation_dict = ObsMetadata(orientation_dict)
        # Channel polarity is defined only while creating Instrument object.
        # Don't change assignment order
        self.orientation = Orientation(orientation_dict, selected_channel_modifs,
                                       self.instrument.polarity)

        self.comments = attributes.get("comments", [])
        self.extras = [str(k) + ": " + str(v)
                       for k, v in (attributes.get('extras', {})).items()]
        self.convert_notes_and_extras_to_obspy()
        self.obspy_channel = self.to_obspy(equipment)

    @property
    def channel_id_code(self):
        """
        Uniquely identify channel through orientation and location code

        format: {orientation}-{location}

        :returns: channel code
        """
        if not self.orientation_code:
            msg = 'No orientation code in channel'
            warnings.warn(msg)
            logger.error(msg)
            raise TypeError(msg)

        # If no location, use 00 as default
        return self.orientation_code + "-" + (self.location_code
                                              if self.location_code else "00")

    def get_orientation_code(self, orientation_dict):
        """
        Get the orientation code from a dict that may include azimuth and dip
        """
        if isinstance(orientation_dict, str):
            keys = orientation_dict
        else:
            keys = list(orientation_dict.keys())
        # There should be only one key
        return keys[0]

    def get_selected_channel_modifs(self, id_code, channel_modifs):
        """
        Select a channel_modification by id_code and channel label.

        Args:
            id_code (str): {orientation_code}-{location_code} for the given
                channel
            channel_modifs (dict): channel modifications to apply, keys
                can be, in order of priority:
                    "<RNT>-"<LOC>" or "<RNT>": Apply to orientation <RNT> (and location <LOC>)
                    "*"-"<LOC>": Apply to all orientations with location code <LOC>
                    "<RNT>"-"*": Apply to all locations with orientation code <RNT>
                   "*" or "*-*": Apply to all ``id_codes``

        Returns:
            the selected channel modification
        """
        # Get general default
        default = channel_modifs.get("*", channel_modifs.get("*-*", {}))
        # Get defaults by location and orientation
        default_by_loc = channel_modifs.get(self.orientation_code + "-*", {})
        default_by_orient = channel_modifs.get("*-" + self.location_code, {})
        # Get modifications specifically for this channel
        chmod = channel_modifs.get(id_code, channel_modifs.get(id_code[:1], {}))

        # Gather all modifications in a single dict, respecting priority order
        # THIS ONLY GOES DOWN ONE LEVEL!!!!!
        for k, v in default_by_loc.items():
            if k not in chmod:
                chmod[k] = v
        for k, v in default_by_orient.items():
            if k not in chmod:
                chmod[k] = v
        for k, v in default.items():
            if k not in chmod:
                chmod[k] = v
        return chmod

    def complete_channel(self, das_channel, channel_default):
        """
        Complement fields defined for each das channel

        Takes all the fields defined for each das channel and complementa them
        with the channel_default fields. If das_channel key exists, leave the
        corresponding value. If not, add channel_default key/value

        :param das_channel: channel to be completed with default
        :type das_channel: dict or object of :class:`ObsMetadata`
        :param channel_default: default that will complement attributes not
            present in ``das_channel``
        :type channel_default: dict or object of :class:`ObsMetadata`
        """
        # If there are no modifications, use default
        if not das_channel:
            return channel_default

        # First fill out allt he channel attributes
        # Only get channel template if das_channel attribute does not exist
        for k, v in channel_default.items():
            if k not in das_channel:
                das_channel[k] = v

        return das_channel

    def __repr__(self):
        s = f'\n\n\nChannel({self.channel_id_code}, '
        s += f'orientation code="{self.orientation.orientation_code}"'
        if self.location:
            s += f',location={self.location}'

        if self.start_date:
            s += f', startdate={self.start_date}'

        if self.end_date:
            s += f', enddate={self.end_date}'
        s += ')'
        return s

    def channel_code(self, sample_rate):
        """
        Return channel code for a given sample rate.

        Validates instrument and orientation codes according to FDSN
        specifications (for instruments, just the length). Channel codes
        specified by user are indicative and are refined using actual sample
        rate.

        :param sample_rate: instrumentation sampling rate (sps)i
        :type sample_rate: float
        """
        inst_code = self.instrument.sensor.seed_instrument_code

        if len(inst_code) != 1:
            msg = f'Instrument code "{inst_code}" is not a single letter'
            warnings.warn(msg)
            logger.error(msg)
            raise ValueError(msg)
        if self.orientation.orientation_code not in ["X", "Y", "Z", "1", "2",
                                                     "3", "H", "F"]:
            msg = f'Orientation code "{self.orientation_code}" is not a '\
                  'valid letter'
            warnings.warn(msg)
            logger.error(msg)
            raise ValueError(msg)

        band_code = self._band_code_validation(sample_rate)
        # print(f'{sample_rate=}, {band_code=}, {inst_code=}, {self.orientation.orientation_code=}')
        return (band_code + inst_code + self.orientation.orientation_code)

    def _band_code_validation(self, sample_rate):
        """
        Return the channel band code corresponding to a sample rate

        :param sample_rate: sample rate (sps)
        :type sample_rate: float
        """
        bbc = self.instrument.sensor.seed_band_base_code
        if len(bbc) != 1:
            msg = f'Band base code "{bbc}" is not a single letter'
            warnings.warn(msg)
            logger.error(msg)
            raise ValueError(msg)
        if bbc in "FCHBMLVUWRPTQ":
            if sample_rate >= 1000:
                return "F"
            elif sample_rate >= 250:
                return "C"
            elif sample_rate >= 80:
                return "H"
            elif sample_rate >= 10:
                return "B"
            elif sample_rate > 1:
                return "M"
            elif sample_rate > 0.3:
                return "L"
            elif sample_rate >= 0.1:
                return "V"
            elif sample_rate >= 0.01:
                return "U"
            elif sample_rate >= 0.001:
                return "W"
            elif sample_rate >= 0.0001:
                return "R"
            elif sample_rate >= 0.00001:
                return "P"
            elif sample_rate >= 0.000001:
                return "T"
            else:
                return "Q"
        elif bbc in "GDES":
            if sample_rate >= 1000:
                return "G"
            elif sample_rate >= 250:
                return "D"
            elif sample_rate >= 80:
                return "E"
            elif sample_rate >= 10:
                return "S"
            else:
                msg = "Short period sensor sample rate < 10 sps"
                warnings.warn(msg)
                logger.warning(msg)
                return "S"  # Return a code anyway
        else:
            msg = f'Unknown band base code: "{bbc}"'
            warnings.warn(msg)
            logger.error(msg)
            raise TypeError(msg)

    @property
    def seed_code(self):
        """
        This is equivalent to channel code
        """
        return self.channel_code()

    def to_obspy(self, equipment):
        """
         Create obspy Channel object

         Returns:
            (~class:`obspy.core.inventory.channel.Channel`)
        """
        # FDSN StationXML spec (and therefore obspy) identifies channels by
        # SEED code, different from  obsinfo (first, identification by
        # arbitrary label, then identification by orientation-location
        code = self.channel_code(self.instrument.sample_rate)

        preamp = self.instrument.preamplifier.obspy_equipment \
            if self.instrument.preamplifier else None
        comments = [Comment(s) for s in self.comments]
        equipments = [equipment]  # TFrom instrumentation equipment

        channel = obspy_Channel(
            code, self.location_code,
            latitude=self.location.obspy_latitude,
            longitude=self.location.obspy_longitude,
            elevation=self.location.obspy_elevation,
            depth=self.location.depth_m,
            azimuth=self.orientation.azimuth,
            dip=self.orientation.dip,
            types=['CONTINUOUS', 'GEOPHYSICAL'],
            external_references=None,
            sample_rate=self.instrument.sample_rate,
            sample_rate_ratio_number_samples=None,
            sample_rate_ratio_number_seconds=None,
            storage_format=None,
            clock_drift_in_seconds_per_sample=1 / (1e8 * float(self.instrument.sample_rate)),
            calibration_units=None, calibration_units_description=None,
            sensor=self.instrument.sensor.obspy_equipment,
            pre_amplifier=preamp,
            data_logger=self.instrument.datalogger.obspy_equipment,
            equipments=equipments,
            response=self.instrument.obspy_response,
            # description=self.channel_id_code,
            comments=comments,
            start_date=self.start_date,  # OJO: will probably be deprecated
            end_date=self.end_date,
            restricted_status=None,
            alternate_code=None,
            historical_code=None,
            data_availability=None,
            identifiers=None,
            water_level=None,
            source_id=None)
        return channel

    def convert_notes_and_extras_to_obspy(self):
        """
        Convert notes and extras to comments.

        In StationXML comments are found at the channel level and up.
        """
        if self.extras:
            if isinstance(self.extras, list):
                self.comments.extend([f'Extra attribute: {{{e}}}' for e in self.extras])
            else:
                self.comments.append(f'Extra attribute: {{{self.extras}}}')
