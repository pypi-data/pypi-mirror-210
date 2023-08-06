"""
Orientation class
"""
# Standard library modules
import warnings
import logging

# Non-standard modules
import obspy.core.util.obspy_types as obspy_types

# obsinfo modules
from obsinfo.obsMetadata.obsmetadata import (ObsMetadata)

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class Orientation(object):
    """
    Class for sensor orientations. No channel modifs. Cannot change orientation
    as it is part of the channel identifiers. Azimuth and dip can be changed
    Orientation is coded by `FDSN standard <http://docs.fdsn.org/projects/
    source-identifiers/en/v1.0/channel-codes.html>`

    Attributes:
        azimuth (degrees): azimuth, clockwise from north
        azimuth_uncertainty (degrees) - For OBS, uncertainty is usually 180º
        dip (degrees): dip,  -90 to 90: positive=down, negative=up
        type dip_uncertainty (degrees)- For OBS, uncertainty is usually 180º
    """

    def __init__(self, attributes_dict, channel_modifs, polarity):
        """
        Constructor

        :Seismometer: If a positive voltage corresponds to upward motion
            (typical vertical seismometer), dip = -90º (up).  If positive
            voltage corresponds to downward motion (typical vertical geophone),
            dip = 90º
        :Hydrophone:  If a positive voltage corresponds to a positive
            (compressional) pressure, then dip = -90º.  If a positive voltage
            corresponds to a decrease in pressure, then dip = 90°

        Args:
            attributes_dict (dict or :class:`.ObsMetadata`): operator information
        """

        if not attributes_dict:
            msg = 'No orientation'
            warnings.warn(msg)
            logger.error(msg)
            raise ValueError(msg)

        # if a dictionary attributes_dict contains azimuth and/of dip info
        # else it's a simple string and is included in a list for generality
        keys = list(attributes_dict.keys()
                    if isinstance(attributes_dict, dict) else attributes_dict)
        if "1" in keys:
            self.orientation_code = "1"
            value = ObsMetadata(attributes_dict.get("1", None))
            if not value:
                msg = 'Type "1" channel has no azimuth'
                warnings.warn(msg)
                logger.error(msg)
                raise ValueError(msg)
            azimuth, azimuth_uncertainty = self.get_value_with_uncertainty(
                value.get_configured_element('azimuth.deg', channel_modifs,
                                             {}, None))
            if azimuth is None:
                msg = 'Type "1" channel has no azimuth'
                warnings.warn(msg)
                logger.error(msg)
                raise ValueError(msg)
            dip, dip_uncertainty = [0, None]
        elif "2" in keys:
            self.orientation_code = "2"
            value = ObsMetadata(attributes_dict.get("2", None))
            if not value:
                msg = 'Type "2" channel has no azimuth'
                warnings.warn(msg)
                logger.error(msg)
                raise ValueError(msg)
            azimuth, azimuth_uncertainty = self.get_value_with_uncertainty(
                value.get_configured_element('azimuth.deg', channel_modifs,
                                             {}, None))
            if azimuth is None:
                msg = 'Type "2" channel has no azimuth'
                warnings.warn(msg)
                logger.error(msg)
                raise ValueError(msg)
            dip, dip_uncertainty = [0, None]
        elif "3" in keys:
            self.orientation_code = "3"
            value = ObsMetadata(attributes_dict.get("3", None))
            if not value:
                msg = 'Type "3" channel has no dip'
                warnings.warn(msg)
                logger.error(msg)
                raise ValueError(msg)
            azimuth, azimuth_uncertainty = [0, None]
            dip, dip_uncertainty = self.get_value_with_uncertainty(
                value.get_configured_element('dip.deg', channel_modifs,
                                             {}, None))
            if dip is None:
                msg = 'Type "3" channel has no dip'
                warnings.warn(msg)
                logger.error(msg)
                raise ValueError()
        elif "H" in keys:
            self.orientation_code = "H"
            azimuth, azimuth_uncertainty = [0, None]
            dip, dip_uncertainty = [90 * polarity, 5]
        elif "X" in keys:
            self.orientation_code = "X"
            azimuth, azimuth_uncertainty = [0, 5]  # Defined by FDSN
            dip, dip_uncertainty = [0, None]
        elif "Y" in keys:
            self.orientation_code = "Y"
            azimuth, azimuth_uncertainty = [90, 5]  # Defined by FDSN
            dip, dip_uncertainty = [0, None]
        elif "Z" in keys:
            self.orientation_code = "Z"
            azimuth, azimuth_uncertainty = [0, None]  # Defined by FDSN
            dip, dip_uncertainty = [90 * polarity, 5]
        else:
            msg = 'Type(s) "{keys}" orientation subcode(s) not implemented'
            warnings.warn(msg)
            logger.error(msg)
            raise ValueError()

        self.azimuth = obspy_types.FloatWithUncertaintiesAndUnit(
            azimuth, lower_uncertainty=azimuth_uncertainty,
            upper_uncertainty=azimuth_uncertainty, unit='degrees')
        self.dip = obspy_types.FloatWithUncertaintiesAndUnit(
            dip, lower_uncertainty=dip_uncertainty,
            upper_uncertainty=dip_uncertainty, unit='degrees')

    def __repr__(self):
        s = '\nOrientation('
        if self.azimuth:
            s += f', Azimuth={self.azimuth}'
        if self.dip:
            s += f', Dip={self.dip}'

        return s

    def get_value_with_uncertainty(self, info_list):
        """
        Validate that info_list is a 2 member list.

        Args:
            info_list (list of strings or floats): two numbers, a value and
                an uncertainty
        Returns:
            (list): the two members
        Raises:
            ValueError if not a list of two floats or strings that can be
                converted to floats
        """

        try:
            if not info_list or not isinstance(info_list, list) \
                    or len(info_list) != 2 \
                    or not isinstance(float(info_list[0]), float):
                msg = f"value and uncertainty or both are illegal {info_list}"
                warnings.warn(msg)
                logger.error(msg)
                raise ValueError(msg)
        except ValueError:
            msg = f"value or uncertainty or both are illegal {info_list}"
            warnings.warn(msg)
            logger.error(msg)
            raise ValueError(msg)
        if info_list[1] is not None:
            if not isinstance(float(info_list[1]), float):
                msg = f"value and uncertainty or both are illegal {info_list}"
                warnings.warn(msg)
                logger.error(msg)
                raise ValueError(msg)
        return [info_list[0], info_list[1]]
