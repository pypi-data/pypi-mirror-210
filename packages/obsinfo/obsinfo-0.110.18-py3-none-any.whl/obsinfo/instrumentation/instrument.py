"""
Instrument and Operator classes
"""
# Standard library modules
import warnings
import logging

# Non-standard modules
from obspy.core.inventory.response import (Response, InstrumentSensitivity
                                           as obspy_Sensitivity)

# obsinfo modules
from .instrument_component import (InstrumentComponent)

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class Instrument(object):    # Was a Channel subclass, but don't see why
    """
    An instrument is an ensemble of a sensor, a datalogger and possibly a
    preamplifier. It also includes a selected configuration for each one of
    these instrument components.

    Attributes:
        datalogger (:class:`Datalogger`)
        sensor: (:class:`Sensor`)
        preamplifier: (:class:`Preamplifier`)
        sample_rate (float): from datalogger sample rate
        delay_correction (float): from datalogger delay correction
        seed_band_base_code (str): from sensor band base code
        seed_instrument_code (str): from sensor instrument code
        seed_orientation (str): from orientation in the channel itself
    """

    def __init__(self, attributes, channel_modifs={}):
        """
        Constructor

        Args:
            attributes (dict of :class:`.ObsMetadata`): instrument attributes
            channel_modifs (dict or :class:`ObsMetadata`):
                modification of attributes per channel specified in stations
        """
        self.correction = None
        self.delay = None

        if not attributes:
            warnings.warn('No instrument attributes')
            logger.error('No instrument attributes')
            raise TypeError()

        # For each InstrumentComponent, strip out and apply
        # "base", "configuration", and "serial_number" keywords
        for ic_type in ('datalogger', 'sensor', 'preamplifier'):
            ic_config_key = ic_type + '_configuration'
            if ic_type in channel_modifs:
                ic_modifs = channel_modifs[ic_type]
                # Pop out keywords
                config = ic_modifs.pop('configuration', None)
                sn = ic_modifs.pop('serial_number', None)
                base = ic_modifs.pop('base', None)
                # replace ic by channel_modifs[ic_type][]'base'] if it exists
                if base is not None:
                    logger.info('Replacing {ic_type}')
                    attributes[ic_type] = base
                if sn is not None:
                    if 'equipment' in ic_modifs:
                        if 'serial_number' in ic_modifs['equipment']:
                            logger.warning('equipment:serial_number and serial_number specified, equipment:serial_number overrides')
                        else:
                            ic_modifs['equipment']['serial_number'] = sn
                    else:
                        ic_modifs['equipment'] = {'serial_number': sn}
                if config is not None:
                    # For now, just replace v0.110 "*_configuration" keyword
                    if ic_config_key in attributes:
                        msg = 'attributes[{}]={} replaced by {{"{}": {{"configuration": {}}}}}'.format(
                            ic_config_key, attributes[ic_config_key], ic_type, config)
                        warnings.warn(msg)
                        logger.warning(msg)
                    attributes[ic_config_key] = config
            config_selector = attributes.get_configured_element(ic_config_key,
                                                                channel_modifs)
            ic_obj = InstrumentComponent.dynamic_class_constructor(
                ic_type, attributes, channel_modifs, config_selector)
            setattr(self, ic_type, ic_obj)  # equivalent to self.ic_type = ic_obj
        # add the three component response stages
        self.combine_response_stages()

        # Validate inputs and outputs of complete response sequence and
        # correct delay
        self.integrate_response_stages()
        if self.response_stages is not None:
            self.obspy_stages = [x.to_obspy() for x in self.response_stages]
        else:
            self.obspy_stages = None
        self.obspy_response = self.to_obspy()
        self.add_sensitivity(self.obspy_response)

    def __repr__(self):
        return f'\nInstrument(Polarity="{self.polarity}", '\
               f'Output sample rate={self.total_output_sample_rate})'

    def combine_response_stages(self):
        """
        Adds all response stages as obsinfo and obpsy objects and renumbers
        them
        
        Returns response_stages as a simple list?
        """
        if self.sensor.response_stages is not None:
            response_st = self.sensor.response_stages.stages
        else:
            response_st = []

        if self.preamplifier is not None:
            # print(f'{self.preamplifier=}')
            if self.preamplifier.response_stages is not None:
                response_st += self.preamplifier.response_stages.stages

        if self.datalogger.response_stages is not None:
            response_st += self.datalogger.response_stages.stages

        # Order the stage_sequence_numbers
        if len(response_st) > 0:
            for i in range(len(response_st)):
                response_st[i].stage_sequence_number = i + 1
            self.response_stages = response_st        
        else:
            self.response_stages = None

    def integrate_response_stages(self):
        """
        Integrates the stages with one another

        1) Renumber stages sequentially
        2) Verify/set units and sample rates
        3) Assure same frequency is used for consecutive PZ filters
        4) Calculate global polarity of the whole set of response stages
        5) Set global response delay correction
        6) Validate sample_rate expressed in datalogger component is equal to
           global response sample rate
        """
        # Stack response stages
        stages = self.response_stages
        
        if self.response_stages is None:
            prev_polarity = None
            accum_sample_rate = None
        elif len(stages) == 0:
            prev_polarity = None
            accum_sample_rate = None
        elif len(stages) == 1:
            prev_polarity = stages[0].polarity
            accum_sample_rate = stages[0].output_sample_rate
        else:
            prev_stage = stages[0]
            prev_frequency = prev_stage.filter.normalization_frequency \
                if prev_stage.filter.type == 'PolesZeros' else None
            prev_polarity = prev_stage.polarity
            accum_sample_rate = prev_stage.output_sample_rate

            for this_stage in stages[1:]:
                prev_ssn = prev_stage.stage_sequence_number
                this_ssn = this_stage.stage_sequence_number
                # 2a) Verify continuity of units
                if prev_stage.output_units != this_stage.input_units:
                    msg = "Stage {} and {} units don't match".format(
                        prev_ssn, this_ssn)
                    warnings.warn(msg)
                    logger.error(msg)
                    raise ValueError(msg)

                # 2b) Verify/set continuity of sample rate
                if prev_stage.input_sample_rate:
                    if not this_stage.decimation_factor:
                        msg = ('No decimation factor for stage {}, setting = 1'
                               .format(this_ssn))
                        warnings.warn(msg)
                        logger.warning(msg)
                        this_stage.decimation_factor = 1
                    next_input_rate = (prev_stage.input_sample_rate
                                       / this_stage.decimation_factor)
                    if this_stage.input_sample_rate:
                        if this_stage.output_sample_rate != next_input_rate:
                            msg = ('stage {} sample rate {} != expected {}'
                                   .format(this_ssn,
                                           this_stage.output_sample_rate,
                                           next_input_rate))
                            warnings.warn(msg)
                            logger.error(msg)
                            raise ValueError(msg)
                    else:
                        this_stage.input_sample_rate = accum_sample_rate

                # 2c) Calculate/verify delay and correction
                if this_stage.input_sample_rate:
                    this_stage.calculate_delay()
                if self.correction is None and self.delay is not None:
                    self.correction = self.delay

                # 3) Station XML requires that all PZ stages have the same
                #    normalization frequency.  Check this condition
                if prev_frequency and prev_frequency != 0 \
                        and this_stage.filter.type == 'PolesZeros':
                    if prev_frequency != this_stage.filter.normalization_frequency:
                        msg = ("Normalization frequencies for PZ stages "
                               "{} and {} don't match".format(prev_ssn,
                                                              this_ssn))
                        warnings.warn(msg)
                        logger.warning(msg)
                    prev_frequency = this_stage.filter.normalization_frequency

                # 4) Calculate global polarity
                if not this_stage.polarity:  # default polarity is positive
                    this_stage.polarity = 1

                prev_polarity *= this_stage.polarity

                prev_stage = this_stage
                prev_frequency = (prev_stage.filter.normalization_frequency
                                  if prev_stage.filter.type == 'PolesZeros'
                                  else None)
                accum_sample_rate = prev_stage.output_sample_rate

        # Check global output sample rate
        if not accum_sample_rate == self.sample_rate:
            msg = (f'Datalogger declared sample rate {self.sample_rate} is '
                  'different from calculated overall sample rate of stages '
                  f'{accum_sample_rate}')
            warnings.warn(msg)
            logger.warning(msg)

        # Set global response attributes
        self.polarity = prev_polarity
        self.total_output_sample_rate = accum_sample_rate

    def to_obspy(self):
        """
        Return equivalent obspy class

        Returns:
            ():class:`obspy.core.inventory.response.Response`)
        """
        return Response(resource_id=None,
                        instrument_sensitivity=None,
                        instrument_polynomial=None,
                        response_stages=self.obspy_stages)

    def add_sensitivity(self, obspy_response):
        """
        Adds sensitivity to an obspy Response object
        Based on ..misc.obspy_routines.response_with_sensitivity

        Args:
            obspy_response (:class:`obspy.core.inventory.response.Response`):
        """

        response_stg = self.response_stages
        gain_prod = 1.
        if response_stg is None:
            iu = "None"
            ou = "None"
            iud = "None"
            oud = "None"
            gain_freq = 0
        else:
            iu = response_stg[0].input_units
            ou = response_stg[-1].output_units
            iud = response_stg[0].input_units_description
            oud = response_stg[-1].output_units_description
            # gain_frequency could be provided, according to StationXML, but we
            # assume it's equal to the gain frequency of first stage
            gain_freq = response_stg[0].gain_frequency,

            if "PA" in iu.upper():
                # MAKE OBSPY THINK ITS M/S TO CORRECTLY CALCULATE SENSITIVITY
                sens_iu = "M/S"
            else:
                sens_iu = iu
            for stage in response_stg:
                gain_prod *= stage.gain

        sensitivity = obspy_Sensitivity(gain_prod, gain_freq,
                                        input_units=iu, output_units=ou,
                                        input_units_description=iud,
                                        output_units_description=oud)
        obspy_response.instrument_sensitivity = sensitivity
        obspy_response.instrument_sensitivity.input_units = iu
        obspy_response.instrument_sensitivity.output_units = ou

    def get_response_stage(self, num):
        """
        Returns the response stage in a given position

        Args:
            num (int): stage number, starting with zero and ordered from
                sensor to datalogger
        """
        # All response stages are at the instrument_component level
        stages = self.response_stages
        assert(num <= stages[-1].stage_sequence_number), \
            'response stage out of range: {num}'
        return stages[num]

    @property
    def equipment_datalogger(self):
        return self.datalogger.equipment

    @property
    def equipment_sensor(self):
        return self.sensor.equipment

    @property
    def equipment_preamplifier(self):
        return self.preamplifier.equipment

    @property
    def sample_rate(self):
        return self.datalogger.sample_rate

    @property
    def delay_correction(self):
        return self.delay_correction

    @property
    def seed_band_base_code(self):
        return self.sensor.seed_band_base_code

    @property
    def seed_instrument_code(self):
        return self.sensor.seed_instrument_code

    @property
    def seed_orientation(self):
        """
        Same as orientation. Kept for compatibility.
        """
        return self.orientation
