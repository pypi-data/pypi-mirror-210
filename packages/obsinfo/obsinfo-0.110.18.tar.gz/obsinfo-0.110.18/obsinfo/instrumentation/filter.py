"""
Filter class and subclasses
"""
# Standard library modules
import math as m
import warnings
import logging

# Non-standard modules
# import obspy.core.inventory.response as obspy_response
# from scipy._lib.doccer import extend_notes_in_docstring

# from ..misc.configuration import ObsinfoConfiguration
warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class Filter(object):
    """
    Filter is superclass of all filter classes

    Attributes:
        type (str): filter type
        offset (int): offset is samples to skip at the beggining of a signal
            in digital filters
    """

    def __init__(self, type="PolesZeros", offset=0):
        """
        Constructor

        Args:
            type (str): filter type
            offset (int): samples that an impulse is offset by a digital filter
        """
        self.type = type
        self.offset = offset

    @staticmethod
    def dynamic_class_constructor(attributes_dict, channel_modif={},
                                  selected_config={}, stage_id="-1",
                                  gain_frequency=1.):
        """
        Creates an appropriate Filter subclass from an attributes_dict

        Args:
            attributes_dict (dict or list of dicts): information file
                dictionaries for stages
            channel_modif (dict or :class:`.ObsMetadata`): channel
                modifications inherited from station
            selected_config (dict or :class:`.ObsMetadata`): the configuration
                description that will override or complement default values
            stage_id (int): id of corresponding stage. Used for reporting only
            gain_frequency (float): frequency at which gain was specified.
                Used for PoleZeros Normalization factor/frequency
        Returns:
            (:class:`.Filter`): object of the adequate filter subclass
        Raises:
            (TypeError): if filter type is not valid
        """
        if attributes_dict is None:
            msg = "No attributes in filter"
            logger.error(msg)
            raise TypeError(msg)

        if "type" not in attributes_dict:
            msg = 'No "type" specified for filter in stage #{stage_id}'
            logger.error(msg)
            raise TypeError(msg)
        else:
            filter_type = attributes_dict.get_configured_element(
                'type', channel_modif, selected_config, None)
            if filter_type == 'PolesZeros':
                obj = PolesZeros.dynamic_class_constructor(
                    filter_type, attributes_dict, channel_modif,
                    selected_config, stage_id, gain_frequency)
            elif filter_type == 'FIR':
                obj = FIR.dynamic_class_constructor(
                    filter_type, attributes_dict, channel_modif,
                    selected_config, stage_id)
            elif filter_type == 'Coefficients':
                obj = Coefficients.dynamic_class_constructor(
                    filter_type, attributes_dict, channel_modif,
                    selected_config, stage_id)
            elif filter_type == 'ResponseList':
                obj = ResponseList.dynamic_class_constructor(
                    filter_type, attributes_dict, channel_modif,
                    selected_config, stage_id)
            elif filter_type == 'ADConversion':
                obj = AD_Conversion.dynamic_class_constructor(
                    filter_type, attributes_dict, channel_modif,
                    selected_config, stage_id)
            elif filter_type == 'Analog':
                obj = Analog.dynamic_class_constructor(
                    filter_type, attributes_dict, channel_modif,
                    selected_config, stage_id, gain_frequency)
            elif filter_type == 'Digital':
                obj = Digital.dynamic_class_constructor(
                    filter_type, attributes_dict, channel_modif,
                    selected_config, stage_id)
            else:
                msg = (f'Unknown Filter type: "{filter_type}" in '
                       'stage #{stage_id}')
                logger.error(msg)
                raise TypeError(msg)

        return obj


class PolesZeros(Filter):
    """
    PolesZeros filter

    Attributes:
        transfer_function_type (str): one of  'LAPLACE (RADIANS/SECOND)',
            'LAPLACE (HERTZ)','DIGITAL (Z-TRANSFORM)'
        poles (list of complex numbers)
        zeros (list of complex numbers)
        normalization_frequency (float)
        normalization_factor (float)
    """

    def __init__(self, filter_type,
                 transfer_function_type='LAPLACE (RADIANS/SECOND)',
                 poles=[], zeros=[], normalization_frequency=1.,
                 normalization_factor=None, offset=0, stage_id=-1):
        """
        Constructor

        Args:
            filter_type (str):
            transfer_function_type (str): one of 'LAPLACE (RADIANS/SECOND)',
                'LAPLACE (HERTZ)', 'DIGITAL (Z-TRANSFORM)'
            poles (list): complex numbers specified as [a, b]
            zeros (list): complex numbers specified as [a, b]
            normalization_frequency (float):
            normalization_factor (float):
            offset (int): makes no sens for an analog filter
            stage_id (int): id of corresponding stage. Used for reporting only
        """
        # poles and zeros should be lists of complex numbers
        if transfer_function_type not in ['LAPLACE (RADIANS/SECOND)',
                                          'LAPLACE (HERTZ)',
                                          'DIGITAL (Z-TRANSFORM)']:
            msg = (f'Illegal transfer_function_type in PolesZeros: '
                   f'"{transfer_function_type}" in stage #{stage_id}')
            logger.error(msg)
            raise TypeError(msg)

        self.transfer_function_type = transfer_function_type
        self.poles = poles
        self.zeros = zeros

        self.normalization_frequency = normalization_frequency
        if normalization_frequency and normalization_factor:
            self.normalization_factor = normalization_factor
        elif filter_type == 'Analog':
            self.normalization_factor = 1.0
        else:
            self.normalization_factor = self.calc_normalization_factor(stage_id)
        super().__init__(filter_type, offset)

    @classmethod
    def dynamic_class_constructor(cls, filter_type, attributes_dict,
                                  channel_modif={},
                                  selected_config={}, stage_id=-1,
                                  gain_frequency=1.):
        """
        Create PolesZeros instance from an attributes_dict

        Args:
            filter_type (str): type of filter, necessarily 'PolesZeros'
            attribute_list (dict or list of dicts): information file
                dictionaries for stages
            channel_modif (dict or :class:`.ObsMetadata`): channel
                modifications inherited from station
            selected_config (dict or :class:`.ObsMetadata`): the configuration
                description that will override or complement default values
            stage_id (int): id of corresponding stage. Used for reporting only
            gain_frequency (float): frequency at which gain was specified.
        Returns:
            (:class:`.PolesZeros`)
        """
        obj = cls(filter_type,
                  attributes_dict.get_configured_element(
                      'transfer_function_type', channel_modif, selected_config,
                      'LAPLACE (RADIANS/SECOND)'),
                  [(float(x[0]) + 1j * float(x[1]))
                   for x in attributes_dict.get_configured_element(
                       'poles', channel_modif, selected_config, [])],
                  [(float(x[0]) + 1j * float(x[1]))
                   for x in attributes_dict.get_configured_element(
                       'zeros', channel_modif, selected_config, [])],
                  attributes_dict.get_configured_element(
                      'normalization_frequency', channel_modif, selected_config,
                      gain_frequency),
                  attributes_dict.get_configured_element(
                      'normalization_factor', channel_modif, selected_config,
                      None),
                  attributes_dict.get_configured_element(
                      'offset', channel_modif, selected_config, 0),
                  stage_id)
        return obj

    def __repr__(self):

        s = f'          PolesZeros(Poles={self.poles}, Zeros={self.zeros}, '
        s += f'Normalization Frequency={self.normalization_frequency:g}, '
        s += f'Normalization Factor={self.normalization_factor:g})'
        return s

    def calc_normalization_factor(self, stage_id=-1, debug=False):
        """
        Calculate the normalization factor for a given set of poles-zeros

        The norm factor A0 is calculated such that

        .. parsed-literal::
                                  sequence_product_over_n(s - zero_n)
                       A0 * abs(—--------------------------------------) == 1
                                  sequence_product_over_m(s - pole_m)

            for s_f = i*2pi*f if the transfer function is Laplace in radians
                      i*f if the transfer function is Laplace in Hertz

        There is no calculation for the digital z-transform

        Returns:
            normalization factor as a float or None if not Laplace
        """
        if not self.normalization_frequency:
            msg = ('No normalization frequency for PZ filter in '
                   f'stage #{stage_id}')
            logger.error(msg)
            raise ValueError(msg)

        A0 = 1.0 + (1j * 0.0)
        if self.transfer_function_type == "LAPLACE (HERTZ)":
            s = 1j * self.normalization_frequency
        elif self.transfer_function_type == "LAPLACE (RADIANS/SECOND)":
            s = 1j * 2 * m.pi * self.normalization_frequency
        else:
            msg = ("Don't know how to calculate normalization factor"
                   "for z-transform poles and zeros!")
            warnings.warn(msg)
            logger.warning(msg)
            return None

        for p in self.poles:
            A0 *= (s - p)
        for z in self.zeros:
            A0 /= (s - z)

        if debug:
            msg = f"poles={self.poles}, zeros={self.zeros}, s={s}, A0={A0}"
            print(msg)
            logger.debug(msg)

        A0 = abs(A0)
        return A0


class FIR(Filter):
    """
    FIR Filter

    Attributes:
        symmetry (str): filter symmetry, one of "EVEN", "ODD", "NONE"
        coefficients (list of floats)
        coefficient_divisor (float)
    """

    def __init__(self, filter_type, symmetry, coefficients,
                 coefficient_divisor, offset=0, stage_id=-1):

        """
        Constructor

        Args:
            filter_type (str): type of filter, necessarily 'FIR'
            symmetry (str): filter symmetry, one of "EVEN", "ODD", "NONE"
            coefficients (list): floats
            coefficient_divisor (float):
            offset (int): # of samples filter will offset an impulse
            stage_id (int): id of corresponding stage. Used for reporting only
        """
        self.symmetry = symmetry
        if symmetry not in ['ODD', 'EVEN', 'NONE']:
            msg = f'Illegal FIR symmetry: "{symmetry} in stage #{stage_id}"'
            logger.error(msg)
            raise TypeError()

        # Validate coefficients
        sum_coeff = 0
        coeff_cnt = 0
        for coeff in coefficients:
            sum_coeff += coeff
            coeff_cnt += 1
        if symmetry == 'EVEN':
            sum_coeff *= 2.
            coeff_cnt *= 2
        if symmetry == 'ODD':
            sum_coeff += sum_coeff - coefficients[-1]
            coeff_cnt += coeff_cnt - 1

        coeff = sum_coeff / coefficient_divisor
        coeff = round(coeff, 2)  # check up to two decimal places
        # last conditional verifies that there is at least one coeff
        if coeff != 1 and coeff != 0:
            msg = (f'Coefficient sum "{coeff}" not equal to one, num. '
                   f'coefficient: "{coeff_cnt}" in stage #{stage_id}')
            warnings.warn(msg)
            logger.warning(msg)

        self.coefficients = coefficients
        self.coefficient_divisor = coefficient_divisor

        super().__init__(filter_type, offset)

    @classmethod
    def dynamic_class_constructor(cls, filter_type, attributes_dict,
                                  channel_modif={}, selected_config={},
                                  stage_id=-1):
        """
        Create FIR instance from an attributes_dict

        Args:
            filter_type (str): type of filter, necessarily 'FIR'
            attribute_list (dict or list of dicts): information file
                dictionaries for stages
            channel_modif (dict or :class:`.ObsMetadata`): channel
                modifications inherited from station
            selected_config (dict or :class:`.ObsMetadata`): the configuration
                description that will override or complement default values
            stage_id (int): id of corresponding stage. Used for reporting only
        Returns:
            (:class:`.FIR`)
        """

        offset = attributes_dict.get_configured_element(
            'offset', channel_modif, selected_config, 0)
        if not offset:
            msg = 'No offset in FIR filter'
            logger.error(msg)
            raise TypeError(msg)

        obj = cls(
            filter_type,
            attributes_dict.get_configured_element(
                'symmetry', channel_modif, selected_config, None),
            attributes_dict.get_configured_element(
                'coefficients', channel_modif, selected_config, []),
            attributes_dict.get_configured_element(
                'coefficient_divisor', channel_modif, selected_config, 1.),
            offset)
        return obj

    def __repr__(self):
        s = f'\tFIR("Symmetry={self.symmetry}",'
        s += f' Coefficients={self.coefficients},'
        s += f' Divisor={self.coefficient_divisor})'
        return s


class Coefficients(Filter):
    """
    Coefficients Filter Class

    Attributes:
        transfer_function_type (str): one of "ANALOG (RADIANS/SECOND)",
            "ANALOG (HERTZ)", or "DIGITAL"
        numerator_coefficients (list of floats)
        denominator_coefficients (list of floats)
    """

    def __init__(self, filter_type, transfer_function_type,
                 numerator_coefficients, denominator_coefficients, offset=0):
        """
        Constructor

        Args:
            filter_type (str): type of filter, necessarily 'Coefficients'
            transfer_function_type (str): one of "ANALOG (RADIANS/SECOND)",
                "ANALOG (HERTZ)", or "DIGITAL"
            numerator_coefficients (list): of floats
            denominator_coefficients (list): of floats
            offset (int): samples that an impulse is offset by the filter

        :param filter_type: type of filter, necessarily 'Coefficients'
        :type filter_type: str

        :param offset:
        :type offset: int
        """
        if transfer_function_type not in ["ANALOG (RADIANS/SECOND)",
                                          "ANALOG (HERTZ)",
                                          "DIGITAL"]:
            msg = f'Illegal transfer function type: "{transfer_function_type}"'
            logger.error(msg)
            raise TypeError(msg)

        self.transfer_function_type = transfer_function_type
        self.numerator_coefficients = numerator_coefficients
        self.denominator_coefficients = denominator_coefficients

        super().__init__(filter_type, offset)

    @classmethod
    def dynamic_class_constructor(cls, filter_type, attributes_dict,
                                  channel_modif={},
                                  selected_config={}, stage_id=-1):
        """
        Create Coefficients instance from an attributes_dict

        Args:
            filter_type (str): type of filter, necessarily 'Coefficients'
            attribute_list (dict or list of dicts): information file
                dictionaries for stages
            channel_modif (dict or :class:`.ObsMetadata`): channel
                modifications inherited from station
            selected_config (dict or :class:`.ObsMetadata`): the configuration
                description that will override or complement default values
            stage_id (int): id of corresponding stage. Used for reporting only
        Returns:
            (:class:`.Coefficients`)
        """
        obj = cls(filter_type,
                  attributes_dict.get_configured_element(
                      'transfer_function_type', channel_modif,
                      selected_config, 'DIGITAL'),
                  attributes_dict.get_configured_element(
                      'numerator_coefficients', channel_modif,
                      selected_config, []),
                  attributes_dict.get_configured_element(
                      'denominator_coefficients', channel_modif,
                      selected_config, []),
                  attributes_dict.get_configured_element(
                      'offset', channel_modif, selected_config, 0)
                  )
        return obj

    def __repr__(self):
        s = '          Coefficients("Transfer Function Type='
        s += f'{self.transfer_function_type}", '
        s += f'Numerator={self.numerator_coefficients}, '
        s += f'Denominator={self.denominator_coefficients})'
        return s


class ResponseList(Filter):
    """
    ResponseList Filter

    Attributes:
        response_list (list of floats): list of responses instead of function
            coefficients
    """

    def __init__(self, filter_type, response_list, offset=0):
        """
        Constructor

        Args"
            filter_type (str): type of filter, necessarily 'ResponseList'
            response_list (list): floats specifying response
            offset (int): samples that an impulse is offset by the filter
        """
        self.response_list = response_list
        super().__init__(filter_type, offset)

    @classmethod
    def dynamic_class_constructor(cls, filter_type, attributes_dict,
                                  channel_modif={},
                                  selected_config={}, stage_id=-1):
        """
        Create Response List instance from an attributes_dict

        Args:
            filter_type (str): type of filter, necessarily 'ResponseList'
            attribute_list (dict or list of dicts): information file
                dictionaries for stages
            channel_modif (dict or :class:`.ObsMetadata`): channel
                modifications inherited from station
            selected_config (dict or :class:`.ObsMetadata`): the configuration
                description that will override or complement default values
            stage_id (int): id of corresponding stage. Used for reporting only
        Returns:
            (:class:`.ResponseList`)
        """
        obj = cls(filter_type,
                  attributes_dict.get_configured_element(
                      'elements', channel_modif, selected_config, []),
                  attributes_dict.get_configured_element(
                      'offset', channel_modif, selected_config, 0))
        return obj

    def __repr__(self):
        return f'          ResponseList("{self.response_list}")'


class Analog(PolesZeros):
    """
    Analog Filter (Flat PolesZeros filter)
    """

    def __init__(self, filter_type, offset=0, normalization_frequency=1.):
        """
        Constructor

        Args:
            filter_type (str): necessarily 'Analog'
            offset (int):
            normalization_frequency (float):
        :type offset: int
        """
        # self.poles = []
        # self.zeros = []
        # self.normalization_frequency = 1.
        # self.normalization_factor = None
        # super().__init__(filter_type, "LAPLACE (RADIANS/SECOND)",
        #                  self.poles, self.zeros, self.normalization_frequency,
        #                  self.normalization_factor, offset)
        super().__init__(filter_type, "LAPLACE (RADIANS/SECOND)",
                         [], [], normalization_frequency, None, offset)

    @classmethod
    def dynamic_class_constructor(cls, filter_type, attributes_dict,
                                  channel_modif={},
                                  selected_config={}, stage_id=-1,
                                  gain_frequency=1.):
        """
        Create Analog instance from an attributes_dict

        Args:
            filter_type (str): type of filter, necessarily 'Analog'
            attribute_list (dict or list of dicts): information file
                dictionaries for stages
            channel_modif (dict or :class:`.ObsMetadata`): channel
                modifications inherited from station
            selected_config (dict or :class:`.ObsMetadata`): the configuration
                description that will override or complement default values
            stage_id (int): id of corresponding stage. Used for reporting only
            gain_frequency (float): frequency at which gain was specified.
        Returns:
            (:class:`.Analog`)
        """
        obj = cls(filter_type,
                  attributes_dict.get_configured_element(
                      'offset', channel_modif, selected_config, 0),
                  gain_frequency)
        return obj

    def __repr__(self):
        return '          Analog()'


class Digital(Coefficients):
    """
    Digital Filter (Flat Coefficients filter)
    """

    def __init__(self, filter_type, offset=0):
        """
        Constructor

        :param filter_type: type of filter, necessarily 'Digital'
        :type filter_type: str
        :param offset:
        :type offset: int
        """
        self.transfer_function_type = 'DIGITAL'
        self.numerator_coefficients = [1.0]
        self.denominator_coefficients = []

        super().__init__(filter_type, "DIGITAL", self.numerator_coefficients,
                         self.denominator_coefficients, offset)

    @classmethod
    def dynamic_class_constructor(cls, filter_type, attributes_dict,
                                  channel_modif={},
                                  selected_config={}, stage_id=-1):
        """
        Create Digital instance from an attributes_dict

        Args:
            filter_type (str): type of filter, necessarily 'Digital'
            attribute_list (dict or list of dicts): information file
                dictionaries for stages
            channel_modif (dict or :class:`.ObsMetadata`): channel
                modifications inherited from station
            selected_config (dict or :class:`.ObsMetadata`): the configuration
                description that will override or complement default values
            stage_id (int): id of corresponding stage. Used for reporting only
        Returns:
            (:class:`.Digital`)
        """

        obj = cls(filter_type, attributes_dict.get_configured_element(
            'offset', channel_modif, selected_config, 0))
        return obj

    def __repr__(self):
        return '          Digital()'


class AD_Conversion(Coefficients):
    """
    AD_Conversion Filter (Flat Coefficients filter)

    Attributes:
        input_full_scale (float)
        output_full_scale (float)
    """

    def __init__(self, filter_type, input_full_scale, output_full_scale,
                 offset=0):
        """
        Constructor

        Args:
            filter_type (str): type of filter, necessarily 'ADConversion'
            input_full_scale (float): A/D's input full scale (volts)
            output_full_scale (float): corresponding output full scale (counts)
            offset (int): number of samples that the filter offsets an
                impulse
        """

        self.transfer_function_type = 'DIGITAL'
        self.numerator_coefficients = [1.0]
        self.denominator_coefficients = []
        self.input_full_scale = input_full_scale
        self.output_full_scale = output_full_scale

        super().__init__(filter_type, "DIGITAL",
                         self.numerator_coefficients,
                         self.denominator_coefficients, offset)

    @classmethod
    def dynamic_class_constructor(cls, filter_type, attributes_dict,
                                  channel_modif={}, selected_config={},
                                  stage_id=-1):
        """
        Create AD_Conversion instance from an attributes_dict

        Args:
            filter_type (str): type of filter, necessarily 'ADConversion'
            attribute_list (dict or list of dicts): information file
                dictionaries for stages
            channel_modif (dict or :class:`.ObsMetadata`): channel
                modifications inherited from station
            selected_config (dict or :class:`.ObsMetadata`): configuration
                description to override or complement default values
            stage_id (int): id of corresponding stage. Used for reporting only
        Returns:
            (:class:`.ADConversion`)
        """
        obj = cls(
            filter_type,
            attributes_dict.get_configured_element(
                'input_full_scale', channel_modif, selected_config, None),
            attributes_dict.get_configured_element(
                'output_full_scale', channel_modif, selected_config, None),
            attributes_dict.get_configured_element(
                'offset', channel_modif, selected_config, 0))
        return obj

    def __repr__(self):
        s = f'\tADConversion(Input Full Scale={self.input_full_scale:g}, '
        s += f'Output Full Scale={self.output_full_scale})'
        return s
