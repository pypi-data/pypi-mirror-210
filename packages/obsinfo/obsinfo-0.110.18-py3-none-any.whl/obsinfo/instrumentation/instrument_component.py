"""
InstrumentComponent class and subclasses Sensor, Preamplifier, Datalogger.
Equipment class
"""
# Standard library modules
import warnings
import logging

# Non-standard modules

# obsinfo
from .response_stages import ResponseStages
from .equipment import Equipment
from obsinfo.obsMetadata.obsmetadata import (ObsMetadata)

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class InstrumentComponent(object):
    """
    InstrumentComponent class. Is superclass of all component classes.
    No obspy/StationXML equivalent, because they only specify the whole
    sensor+amplifier+datalogger system

    Attributes:
        equipment (:class:`Equipment`)
        response_stages (:class:`ResponseStages`)
        obspy_equipment (:class:`obspy_Equipment`)
        config_description (str): description of configuration to be added
            to equipment description
    """

    def __init__(self, equipment, response_stages=None,
                 config_description=''):
        """
        Constructor. Invoked by dynamic_class_constructor.

        Args:
            equipment (:class:`Equipment`): equipment features of component
            response_stages (:class:`ResponseStages`): Response of component
                as a list of stages
            config_description (str): description of configuration to be added
                to equipment description
        """
        self.equipment = equipment
        self.config_description = config_description

        # print(f'{response_stages=}')
        if response_stages is None:
            msg = f'response_stages is None {type(self)}'
            warnings.warn(msg)
            logger.warning(msg)
        elif response_stages.stages is None:
            msg = f'response_stages.stages is None {type(self)}'
            warnings.warn(msg)
            logger.warning(msg)
            response_stages = None
        elif not response_stages or not response_stages.stages:
            msg = f'No response stages in {type(self)}'
            warnings.warn(msg)
            logger.error(msg)
            raise TypeError(msg)
        elif not response_stages.stages:
            msg = f'No stages in response_stages in {type(self)}'
            warnings.warn(msg)
            logger.error(msg)
            raise TypeError(msg)
        self.response_stages = response_stages
        if self.config_description:
            self.equipment.description += ' [config: {}]'.format(
                self.config_description)
        self.obspy_equipment = self.equipment.to_obspy()

    def retrieve_configuration(comp_type, attributes_dict,
                               configuration_selection=None):
        """
        Completes the component configuration.

        A configuration selector can be defined in the instrumentation class,
        otherwise a config default is used.  They may be used to select a
        configuration in the list of configuration definitions. If a
        configuration matches the selector configuration its attributes will
        override or add to existing attributes.

        Args:
            comp_type (str): Type of instrument component. Used for messaging
                purposes only
            attributes_dict (dict or :class:`ObsMetadata`): attributes of
                component, hopefully including configuration_default
            configuration_selection (str): label of configuration to be
                selected
        Returns:
            selected configuration, if found. Otherwise, empty dictionary
        """

        if not attributes_dict:
            return {}

        configuration_default = attributes_dict.get('configuration_default',
                                                    None)
        # If there is a selected configuration at the instrumentation level)
        # use it, else use default
        # configuration at component level
        # If no default configuration selected_configuration will be None
        selected_configuration_key = configuration_selection \
            if configuration_selection else configuration_default

        all_configurations = attributes_dict.get('configuration_definitions',
                                                 {})
        if not selected_configuration_key:
            if all_configurations == {}:
                return {}
            else:
                msg = (f'No configuration key or default found in {comp_type}.'
                       ' No configuration definition will be applied')
                warnings.warn(msg)
                logger.warning(msg)
                return {}
        selected_configuration = all_configurations.get(
            selected_configuration_key, {})

        if selected_configuration == {}:
            msg = "{}'s requested configuration ('{}') is not in configuration_definitions: {}".format(
                comp_type, selected_configuration_key,
                [k for k in all_configurations.keys()])
            logger.warning(msg)
            raise TypeError(msg)
        elif selected_configuration is None:  # configuration is there but empty
            selected_configuration = {"configuration_description": selected_configuration_key}
        else:
            if "configuration_description" not in selected_configuration:
                selected_configuration["configuration_description"] = selected_configuration_key

        return selected_configuration

    @staticmethod
    def dynamic_class_constructor(component_type, attributes_dict,
                                  channel_modif={}, config_selector=''):
        """Builds a modified, configured Instrument_component
        
         Passes onto subclass (Sensor, Preamplifier, Datalogger) 
         methods after error checking.

        Args:
            component_type (str): type of component ('sensor', 'datalogger'
                or 'preamplifier')
            attributes_dict (dict or :class:`ObsMetadata`): Instrument
                attributes (with component_type keys)
            channel_modif (dict or :class:`ObsMetadata`): channel modification
                inherited from station (with component_type keys)
            config_selector (str): configuration selector

        Returns:
            object of the adequate subclass
        """
        if not attributes_dict.get(component_type, None):
            if component_type == 'preamplifier':  # Only preamps are optional
                return None
            else:
                msg = f'No {component_type}'
                warnings.warn(msg)
                logger.error(msg)
                raise TypeError(msg)

        selected_config = InstrumentComponent.retrieve_configuration(
            component_type, attributes_dict[component_type], config_selector)

        if component_type == 'datalogger':
            theclass = Datalogger
        elif component_type == 'sensor':
            theclass = Sensor
        elif component_type == 'preamplifier':
            theclass = Preamplifier
        else:
            msg = f'Unknown InstrumentComponent "{component_type}"'
            warnings.warn(msg)
            logger.error(msg)
            raise TypeError(msg)
        obj = theclass.dynamic_class_constructor(
            ObsMetadata(attributes_dict[component_type]),
            channel_modif.get(component_type, {}),
            selected_config)
        return obj

    def __repr__(self):
        s = ''
        if self.equipment.description:
            s += f', description="{self.equipment.description}"'
        if self.response_stages is not None:
            s += f'Response stages: {len(self.response_stages.stages)}'
        return s


class Sensor(InstrumentComponent):
    """
    Sensor Instrument Component. No obspy equivalent

    Attributes:
        seed_band_base_code (str): SEED base code ("B" or "S") indicating
            instrument band.
        seed_instrument_code (str): SEED instrument code

    """
    def __init__(self, equipment, seed_band_base_code, seed_instrument_code,
                 response_stages=None, config_description=''):
        """
        Constructor

        Args:
            equipment (:class:`.Equipment`): Equipment information
            seed_band_base_code (str (len 1)): SEED base code ("B" or "S")
                indicating instrument band.  Must be modified by
                obsinfo to correspond to output sample rate. Actual SEED base
                code is determined by FDSN standard <http://docs.fdsn.org/
                projects/source-identifiers/en/v1.0/channel-codes.html>`
            seed_instrument code(str (len 1)): SEED instrument code, determined
                by `FDSN standard <http://docs.fdsn.org/projects/source-
                identifiers/en/v1.0/channel-codes.html>`
            response_stages (:class:`ResponseStages`): channel modifications
                inherited from station
            config_description (str): the configuration description that was
                selected, to complement component description
        """
        self.seed_band_base_code = seed_band_base_code
        self.seed_instrument_code = seed_instrument_code  # dictionary
        super().__init__(equipment, response_stages, config_description)

    @classmethod
    def dynamic_class_constructor(cls, attributes_dict, channel_modif={},
                                  selected_config={}):
        """
        Create Sensor instance from an attributes_dict

        Args:
            attributes_dict (dict or :class:`ObsMetadata`): attributes of
                component
            channel_modif (dict or :class:`ObsMetadata`): channel modifications
                inherited from station
            selected_config (dict or :class:`ObsMetadata`): the configuration
                description that will override or complement default values
        Returns:
            (:class:`Sensor`)
        """

        if not attributes_dict:
            return None
        if not selected_config:
            # Avoids a syntax error in the yaml file: two consecutive labels
            # with no response stages
            selected_config = {}

        seed_dict = ObsMetadata(attributes_dict).get_configured_element(
            'seed_codes', channel_modif, selected_config, {})

        # The next line of code will totally override response states in
        # attribute_dict IF there is a selected_config with response_stages
        response_stages_list = attributes_dict.get_configured_element(
            'response_stages', {}, selected_config, None)

        response_stages = ResponseStages(
            response_stages_list,
            channel_modif.get('response_modifications', {}),
            selected_config.get('response_modifications', {}),
            None)

        obj = cls(Equipment(ObsMetadata(attributes_dict.get('equipment',
                                                            None)),
                            channel_modif.get('equipment', {}),
                            selected_config.get('equipment', {})),
                  ObsMetadata(seed_dict).get_configured_element(
                      'band_base', channel_modif, selected_config, None),
                  ObsMetadata(seed_dict).get_configured_element(
                      'instrument', channel_modif, selected_config, None),
                  response_stages,
                  attributes_dict.get_configured_element(
                      'configuration_description', channel_modif,
                      selected_config, ''))
        return obj

    def __repr__(self):
        s = ''
        s += f'\nSensor( "band code={self.seed_band_base_code}", '\
             f'"instrument code={self.seed_instrument_code}")'
        s += super().__repr__()
        return s


class Datalogger(InstrumentComponent):
    """
    Datalogger Instrument Component.

    Obspy equivalent is Datalogger, but only contains elements of
    :class:`Equipment`
    """
    def __init__(self, equipment, sample_rate, delay_correction=None,
                 response_stages=None, config_description=''):
        """
        Constructor

        Args:
            equipment (:class:`Equipment`): equipment attributes
            sample_rate (float): sample rate of given configuration. Checked
                against actual sample rate
            delay_correction (float or None): the delay correction of the
                component. If a float, it is applied to the last stage and the
                other stage corrections are set to 0.  If None, each stage's
                correction is set equal to its delay
            response_stages (:class:`ResponseStages`): channel modifications
                inherited from station
            config_description (str): the configuration description that was
                selected, to complement component description
        """
        self.sample_rate = sample_rate
        self.delay_correction = delay_correction
        super().__init__(equipment, response_stages, config_description)

    @classmethod
    def dynamic_class_constructor(cls, attributes_dict, channel_modif={},
                                  selected_config={}):
        """
        Create Datalogger instance from an attributes_dict

        Args:
            attributes_dict (dict or :class:`ObsMetadata`): component
                attributes
            channel_modif (dict or :class:`ObsMetadata`): channel modifications
                inherited from station
            selected_config (dict or :class:`ObsMetadata`): the configuration
                description that will override or complement default values
        Returns:
            (:class:`Datalogger`)
        """
        if not attributes_dict:
            return None
        if not selected_config:
            # Avoids a syntax error in the yaml file: two consecutive labels
            # with no response stages
            selected_config = {}

        sample_rate = attributes_dict.get_configured_element(
            'sample_rate', channel_modif, selected_config, None)
        delay_correction = attributes_dict.get_configured_element(
            'delay_correction', channel_modif, selected_config, None)
        config_description = attributes_dict.get_configured_element(
            'configuration_description', channel_modif, selected_config, '')

        # The next line of code will totally override response states in
        # attribute_dict IF there is a selected_config with response_stages
        response_stages_list = attributes_dict.get_configured_element(
            'response_stages', {}, selected_config, None)

        response_stages = ResponseStages(
            response_stages_list,
            channel_modif.get('response_modifications', {}),
            selected_config.get('response_modifications', {}),
            delay_correction)

        obj = cls(Equipment(ObsMetadata(attributes_dict.get('equipment',
                                                            None)),
                            channel_modif.get('equipment', {}),
                            selected_config.get('equipment', {})),
                  sample_rate,
                  delay_correction,
                  response_stages,
                  config_description)

        return obj

    def __repr__(self):
        s = f'Datalogger(Sample Rate={self.sample_rate})'
        s += super().__repr__()
        return s


class Preamplifier(InstrumentComponent):
    """
    Preamplifier Instrument Component. No obspy equivalent

      Attributes:
        None
    """

    def __init__(self, equipment, response_stages=None, config_description=''):
        """
        Constructor

        Args:
            equipment (:class:`Equipment`): Equipment information
            response_stages (:class:`ResponseStages`): channel modifications
                inherited from station
            config_description (str): the configuration description that was
                selected, added to equipment description
        """
        super().__init__(equipment, response_stages, config_description)

    @classmethod
    def dynamic_class_constructor(cls, attributes_dict, channel_modif={},
                                  selected_config={}):
        """
        Create Preamplifier instance from an attributes_dict

        Args:
            attributes_dict (dict or :class:`ObsMetadata`): attributes of
                component
            channel_modif (dict or :class:`ObsMetadata`): channel modifications
                inherited from station
            selected_config (dict or :class:`ObsMetadata`): the configuration
                description that will override or complement default values
        Returns:
            (:class:`Preamplifier`)
        """

        if not attributes_dict:
            return None
        if not selected_config:
            # Avoids a syntax error in the yaml file: two consecutive labels
            # with no response stages
            selected_config = {}

        # The next line of code will totally override response states in
        # attribute_dict IF there is a selected_config with response_stages
        response_stages_list = attributes_dict.get_configured_element(
            'response_stages', {}, selected_config, None)
        config_description = attributes_dict.get_configured_element(
            'configuration_description', channel_modif, selected_config, '')

        response_stages = ResponseStages(
            response_stages_list,
            channel_modif.get('response_modifications', {}),
            selected_config.get('response_modifications', {}),
            None)

        obj = cls(Equipment(ObsMetadata(attributes_dict.get('equipment',
                                                            None)),
                            channel_modif.get('equipment', {}),
                            selected_config.get('equipment', {})),
                  response_stages,
                  config_description)

        return obj

    def __repr__(self):
        s = 'Preamplifier()'
        s += super().__repr__()
        return s
