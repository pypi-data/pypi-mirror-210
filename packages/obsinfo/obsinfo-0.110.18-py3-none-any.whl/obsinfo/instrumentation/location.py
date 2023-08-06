"""
Location classe
"""
# Standard library modules
import warnings
import numpy as np
import logging

# Non-standard modules
from obspy.core.util.obspy_types import FloatWithUncertaintiesFixedUnit
from obspy.core.inventory.util import (Latitude, Longitude)
# from obspy.geodetics.base import kilometers2degrees


warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class Location(object):
    """
    Location class.

    Attributes:
        latitude (float): station latitude (degrees N)
        longitude (float): station longitude (degrees E)
        elevation (float): station elevation (meters above sea level)
        uncertainties_m (dict): 'lat', 'lon', 'elev' in METERS
        geology (str): site geology
        vault (str): vault type
        depth_m (float): depth of station beneath surface (meters)
        localisation_method (str): method used to determine position
        obspy_latitude: latitude as an *obspy* object
        obspy_longitude: longitude as an *obspy* object

    """

    def __init__(self, attributes_dict):
        """
        Create Location object and assign attributes from attributes_dict.
        Validate required location attributes exist
        Convert to obspy longitude and latitude

        :param attributes_dict: location information
        :type attributes_dict: dict or object of :class:`ObsMetadata`
        """
        position = attributes_dict.get('position', None)
        base = attributes_dict.get('base', None)

        if not base:
            msg = 'No base in location'
            warnings.warn(msg)
            logger.error(msg)
            raise TypeError(msg)
        if not position:
            msg = 'No position in location'
            warnings.warn(msg)
            logger.error(msg)
            raise TypeError(msg)

        self.latitude = position.get('lat', None)
        self.longitude = position.get('lon', None)
        self.elevation = position.get('elev', None)
        self.uncertainties_m = base.get('uncertainties.m', None)
        self.geology = base.get('geology', None)
        self.vault = base.get('vault', None)
        self.depth_m = base.get('depth.m', None)
        self.localisation_method = base.get('localisation_method', None)

    def __repr__(self):
        s = f'Location({self.latitude:g}, {self.longitude:g}, '
        s += f'{self.elevation:g}, {self.uncertainties_m}'
        if not self.geology == 'unknown':
            s += f', "geology: {self.geology}"'
        if self.vault:
            s += f', vault="{self.vault}"'
        if self.depth_m is not None:
            s += f', depth_m={self.depth_m:g}'
        if self.localisation_method:
            s += f', localisation_method="{self.localisation_method}"'
        s += ')'
        return s

    @property
    def obspy_elevation(self):
        """
        Returns elevation as obspy FloatWithUncertaintiesFixedUnit object
        """
        return FloatWithUncertaintiesFixedUnit(
            value=self.elevation,
            lower_uncertainty=self.uncertainties_m.get('elev', None),
            upper_uncertainty=self.uncertainties_m.get('elev', None),
            measurement_method=self.localisation_method)

    @property
    def obspy_latitude(self):
        """
        Returns obspy Latitude object
        """
        uncert_m = self.uncertainties_m.get('lat', None) \
            if self.uncertainties_m else None
        if uncert_m is None:
            lat_uncert = None
        else:
            meters_per_degree_lat = 1852.0 * 60.0
            # lat_uncert = kilometers2degrees(uncert_m / 1000)
            lat_uncert = uncert_m / meters_per_degree_lat
            lat_uncert = float("{:.3g}".format(lat_uncert))
        return Latitude(value=self.latitude,
                        lower_uncertainty=lat_uncert,
                        upper_uncertainty=lat_uncert)

    @property
    def obspy_longitude(self):
        """
        Returns obspy Longitude object
        """

        uncert_m = self.uncertainties_m.get('lon', None) \
            if self.uncertainties_m else None
        if uncert_m is None or abs(self.latitude) == 90:
            lon_uncert = None
        else:
            # lon is along parallel, not a great circle, so we must reduce by
            # cosine.
            meters_per_degree_lon = 1852.0 * 60.0 * np.cos(self.latitude * np.pi / 180.0)
            # lon_uncert = kilometers2degrees(
            #     (uncert_m / 1000) * np.cos(np.radians(self.latitude)))
            lon_uncert = uncert_m / meters_per_degree_lon
            lon_uncert = float("{:.3g}".format(lon_uncert))
        return Longitude(value=self.longitude,
                         lower_uncertainty=lon_uncert,
                         upper_uncertainty=lon_uncert)

    @staticmethod
    def get_location_from_code(locations, code, type, label):
        """
        Obtain from the locations dictionary one location by code (key).
        Raise exception if not found
        """
        if not locations:
            msg = 'No locations specified in station'
            warnings.warn(msg)
            logger.error(msg)
            raise TypeError(msg)

        loc = locations.get(code, None)

        if not loc:
            if type == 'station':  # station location code is mandatory
                msg = f'Location "{code}" not found in station {label}'
                warnings.warn(msg)
                logger.error(msg)
                raise TypeError(msg)
            else:
                msg = f'Channel {label} has no location code. Assuming '\
                      'location code "00"'
                warnings.warn(msg)
                logger.warning(msg)

                loc = locations.get("00", None)
                if not loc:
                    msg = f'Location "{code}" not found in channel {label}'
                    warnings.warn(msg)
                    logger.error(msg)
                    raise TypeError(msg)
        return loc
