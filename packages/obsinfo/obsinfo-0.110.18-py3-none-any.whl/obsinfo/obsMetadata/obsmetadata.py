"""
obsinfo information file routines, contained in superclass ObsMetadata for
generality
"""
# Standard library modules
import json
from pathlib import Path, PurePath
import sys
import re
import warnings
from urllib.parse import urlparse
from urllib.parse import unquote
import logging

# Non-standard modules
import jsonschema
import yaml

# Local modules
from obsinfo.misc import yamlref
from obsinfo.misc.yamlref import JsonLoader
from obsinfo.misc.remoteGitLab import gitLabFile
from obsinfo.misc.discoveryfiles import Datapath

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")

root_symbol = "#"
VALID_FORMATS = ["JSON", "YAML"]
VALID_TYPES = ["author",
               "datacite",
               "datalogger",
               "filter",
               "instrumentation",
               "location_base",
               "network_info",
               "network",
               "operator",
               "preamplifier",
               "sensor",
               "stage",
               "station",
]


class ObsMetadata(dict):
    def __init__(self, *args, **kwargs):
        """
        Constructor, simply create a dict with positional and keyword arguments

        Args:
            args (*list): positional arguments
            kwargs (**dict): keyword arguments
        """
        super().__init__(*args, **kwargs)

    def convert_to_obsmetadata(self):
        """
        Make all contained dictionaries objects of :class: `.ObsMetadata`
        """

        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = self.__class__(value)
                self[key].convert_to_obsmetadata()
            elif isinstance(value, list):
                for x in value:
                    if isinstance(x, dict):
                        x = self.__class__(x)
                        x.convert_to_obsmetadata()

    def list_valid_types():
        """
        Returns a list of valid information file types

        :returns: list of valid information file types
        """
        return VALID_TYPES

    @staticmethod
    def is_valid_type(type):
        """
        Returns true if input is a valid schema type
        """
        return type in VALID_TYPES

    def validate(self, schemas_path, filename, remote=False, format=None,
                 file_type=None, verbose=False, schema_file=None, quiet=False,
                 dp=None):
        """
        Validates a YAML or JSON file against schema

        Args:
            schemas_path (str): path to schema files
            filename (str or path-like): name of file to validate
            remote (bool): whether to search for filename in a remote
                repository
            format (str): format of information file:  "JSON" or "YAML"
            file_type (str): type of info file: "network", "station",
                "instrumentation", "datalogger", "preamplifier", "sensor",
                "stage", "filter"
            verbose (bool): Print progression of validation steps with
                filenames
            schema_file (str): name (without path) of schema file
            quiet (bool): Deprecated. Conserved for compatibility. Cancels
                verbose.
            dp (Datapath): datapath for information files.  If None,
                defaults to values stored in .obsinforc

        If file_type and/or format are not provided, tries to figure them out
        from the filename, which should end with "*{FILETYPE}.{FORMAT}*
        """
        if quiet:
            verbose = False

        if not file_type and not schema_file:
            file_type = ObsMetadata.get_information_file_type(filename)

        msg = f"instance = {filename}"
        logger.info(msg)
        if verbose:
            print(msg)

        if dp is None:
            dp = Datapath()  # Datapath for information files, not schemas

        instance = (ObsMetadata.read_json_yaml_ref(filename, dp, format)
                    if not remote else
                    ObsMetadata.read_json_yaml_ref_datapath(filename, dp,
                                                            format))

        base_file = (file_type + '.schema.json' if not schema_file else schema_file)
        if ".schema.json" not in base_file:
            base_file += '.schema.json'
        schema_fullpath = PurePath(schemas_path) / base_file
        base_uri = unquote(PurePath(schema_fullpath).as_uri())

        schema_datapath = Datapath(schemas_path)
        try:
            with open(schema_fullpath, "r") as f:
                try:
                    s=f.read()
                except Exception as e:
                    msg = str(e)
                    logger.error(msg)
                    print(msg)
                    return False
                try:
                    schema = yamlref.loads(
                        s, base_uri=base_uri, jsonschema=True,
                        datapath=schema_datapath, recursive=True)
                except json.decoder.JSONDecodeError as e:
                    msg = ("JSONDecodeError: Error loading JSON schema "
                           f"file: {schema_fullpath}")
                    logger.error(msg)
                    print(msg)
                    logger.error(str(e))
                    print(str(e))
                    return False
                except BaseException as err:
                    msg = f"{type(err)}: Error loading JSON schema file: {schema_fullpath}"
                    print(msg)
                    logger.error(msg)
                    print(err)
                    logger.error(err)
                    return False
        except FileNotFoundError:
            msg = f'File not found: {schema_fullpath}'
            logger.error(msg)
            raise FileNotFoundError(msg)
        except (IOError, OSError):
            msg = f'Input/Output error with file: {schema_fullpath}'
            print(msg)
            logger.error(msg)
            raise

        # Lazily report all errors in the instance
        # ASSUMES FIXED SCHEMA (I couldn't get it to work otherwise)
        try:
            msg1 = f"schema =   {schema_fullpath.name}"
            msg2 = "\tTesting schema ..."
            logger.info(msg1)
            logger.info(msg2)
            if verbose:
                print(msg1)
                print(msg2, end="")

            # Check schema first
            jsonschema.Draft7Validator.check_schema(schema)

            msg1 = "OK"
            msg2 = "\tTesting instance ..."
            logger.info(msg1)
            logger.info(msg2)
            if verbose:
                print(msg1)
                print(msg2, end="")

            v = jsonschema.Draft7Validator(schema)

            if not v.is_valid(instance):
                if not quiet:
                    print("")
                errors = sorted(v.iter_errors(instance), key=lambda e: e.path)
                for error in errors:
                    if not quiet:
                        print("\t\t", end="")
                    for elem in error.path:
                        msg = f"['{elem}']"
                        if not quiet:
                            print(msg, end="")
                            logger.error(msg)
                    msg = f": {error.message}"
                    if not quiet:
                        print(msg)
                        logger.error(msg)
                if not quiet:
                    print("\tFAILED")
                    logger.info("\tFAILED")
                return False
            else:
                if verbose:
                    print("OK")
                logger.info("OK")
                return True
        except jsonschema.ValidationError as e:
            logger.error(e.message)
            if not quiet:
                print("\t" + e.message)
            return False

    def get_information_file_format(filename):
        """
        Determines if the information file is in JSON or YAML format.

         Assumes that the filename is "*.{FORMAT}*

        Args:
            filename (str): filename to determine the type of
        Returns:
            format
        Raises:
            (ValueError): on unknown format
        """
        suffix = PurePath(filename).suffix
        format = suffix[1:].upper()
        if format in VALID_FORMATS:
            return format
        msg = f"Unknown format: {format}"
        print(msg)
        logger.error(msg)
        raise ValueError(msg)

    def get_information_file_type(filename):
        """
        Determines the type of a file.

        Assumes that the filename is "*.{TYPE}.{SOMETHING}*

        Args:
            filename (str): filename to determine the type of
        Returns:
            (str): file type
        Raises:
            ValueError
        """
        stem = PurePath(filename).stem
        suffix = PurePath(stem).suffix
        type = suffix[1:]
        print(f'{stem=}, {suffix=}, {type=}')
        if type in VALID_TYPES:
            return type
        msg = f"File '{filename}' is of unknown type: {type}"
        print(msg)
        logger.error(msg)
        raise ValueError(msg)

    def read_json_yaml(filename, format=None):
        """
        Reads a JSON or YAML file. Does NOT use jsonReference  DEPRECATED.

        DEPRECATED. Not being used by any obsinfo method or function. Kept
        for compatibility

        Args:
            filename (str): filename
            format (str): format type, either "YAML" or "JSON"
        Returns:
            (dict):  JSON or YAML parsed information files
        Raises:
            (JSONDecodeError): problem with JSON read
            (FileNotFoundError): file not found
            (IOError): File input/output erre
        """
        if not format:  # validate format is legal. Otherwise program will exit
            format = ObsMetadata.get_information_file_format(filename)

        with open(filename, "r") as f:
            if format == "YAML":
                try:
                    element = yaml.safe_load(f)
                except Exception:
                    msg = f"Error loading YAML file: {filename}"
                    print(msg)
                    logger.error(msg)
                    raise ValueError
            else:
                try:
                    element = json.load(f)
                except json.JSONDecodeError as e:
                    msg = ("JSONDecodeError: Error loading JSON file: "
                           f"{filename}: {str(e)}")
                    print(msg)
                    logger.error(msg)
                except Exception:
                    msg = f"Error loading JSON file: {filename}"
                    print(msg)
                    logger.error(msg)
                    raise
        return element

    def read_json_yaml_ref_datapath(filename, datapath, format=None):
        """
        Reads a JSON or YAML file using jsonReference using OBSINFO_DATAPATH

        Args:
            filename (str): filename
            datapath (:class:`.Datapath`): list of directories to search
                for info files
            format(str): format type, either "YAML" or "JSON"
        Returns:
            (dict):  JSON or YAML parsed information files
        Raises:
            (JSONDecodeError): problem with JSON read
            (FileNotFoundError): file not found
            (IOError): File input/output erre
        """

        if not format:
            format = ObsMetadata.get_information_file_format(filename)

        bu = unquote(filename)

        if gitLabFile.isRemote(bu):
            base_uri = unquote(urlparse(bu).path)
            loader = JsonLoader()
            jsonstr = loader.get_json_or_yaml(bu, base_uri=base_uri,
                                              datapath=datapath)
            return yamlref.loads(jsonstr, base_uri=base_uri, datapath=datapath)
        else:
            base_uri = Path(bu).as_uri()
            try:
                with open(unquote(filename), "r") as f:
                    return yamlref.load(f, base_uri=base_uri,
                                        datapath=datapath)
            except FileNotFoundError:
                msg = f'File not found: {filename}'
                logger.error(msg)
                raise FileNotFoundError(msg)
            except (IOError, OSError):
                msg = f'Input/Output error with file: {filename}'
                print(msg)
                logger.error(msg)
                raise

    def read_json_yaml_ref(filename, datapath, format=None):
        """
        Reads a JSON or YAML file using jsonReference

        Like read_json_yaml_ref, but does not look for files in
        OBSINFO_DATAPATH
        $ref within the data files without absolute or relative path will be
        still looked for in OBSINFO_DATAPATH

        Args:
            filename (str): filename
            datapath (:class:`.Datapath`): object to store list of
            directories to search info files. Used as a dummy.
            format (str): format type, either "YAML" or "JSON"
        Returns:
            (dict): JSON or YAML parsed information files
        Raises:
            (JSONDecodeError): problem with JSON read
            (FileNotFoundError): file not found
            (IOError): File input/output erre
        """
        if not format:
            format = ObsMetadata.get_information_file_format(filename)

        bu = unquote(filename)
        base_uri = Path(bu).as_uri()

        try:
            with open(filename, "r") as f:
                return yamlref.load(f, base_uri=base_uri, datapath=datapath)
        except FileNotFoundError:
            msg = f'File not found: {filename}'
            print(msg)
            logger.error(msg)
            raise FileNotFoundError(msg)
        except (IOError, OSError):
            msg = f'Input/Output error with file: {filename}'
            print(msg)
            logger.error(msg)
            raise

    @staticmethod
    def read_info_file(filename, datapath, remote=False, validate=True,
                       format=None, verbose=False):
        """
        Reads an information file

        Args:
            filename (str): filename
            datapath (:class:`.Datapath`): stores list of directories to
                search info files
            validate (bool): validate before reading
            remote (bool): whether to use absolute/relative path locally
                or OBSINFO_DATAPATH
            format (str): format type ("YAML" or "JSON")

        Returns:
            (:class:`ObsMetadata`): JSON or YAML parsed info files
        """
        if validate:
            if verbose:
                print(f'Validating network file: {filename}')
            logger.info(f'Validating network file: {filename}')
            ObsMetadata().validate(
                Path(__file__).parent.parent.joinpath('data', 'schemas'),
                str(filename), remote=remote, verbose=verbose)
        dict = (ObsMetadata.read_json_yaml_ref(filename, datapath, format)
                if not remote else
                ObsMetadata.read_json_yaml_ref_datapath(filename, datapath,
                                                        format))
        # Create an ObsMedatada object, which is a dir with some added methods
        return ObsMetadata(dict)

#     def _validate_script(argv=None):
#         """
#         Validate an obsinfo information file
#
#         Validates a file named *.{TYPE}.json* or *.{TYPE}.yaml* against the
#         obsinfo schema.{TYPE}.json file.
#
#         {TYPE} can be campaign, network, instrumentation,
#             instrument_components or response
#         """
#         from argparse import ArgumentParser
#
#         parser = ArgumentParser(prog="obsinfo-validate", description=__doc__)
#         parser.add_argument("info_file", help="Information file")
#         parser.add_argument("-t", "--type", choices=VALID_TYPES,default=None,
#                             help="Forces information file type (overrides "
#                                  "interpreting from filename)")
#         parser.add_argument("-f", "--format", choices=VALID_FORMATS,
#                             default=None,
#                             help="Forces information file format (overrides "
#                                  "interpreting from filename)")
#         parser.add_argument("-s", "--schema", default=None,
#                             help="Schema file (overrides interpreting from "
#                                  "filename)")
#         parser.add_argument("-v", "--verbose", action="store_true",
#                             help="increase output verbosity")
#         args = parser.parse_args()
#         validate(args.info_file, format=args.format, type=args.type,
#                  schema_file=args.schema, verbose=args.verbose)

    def get_configured_element(self, key, channel_modification={},
                               selected_configuration={}, default=None):
        """
        Substitute an ObsMetadata element with selected or modification values

        This is the heart of *obsinfo* flexibility, which permits changes in
        configuration or even in individual attributes via channel
        modifications.

        Returns the value corresponding to key in the following priority:

        1) channel_modification[key]
        2) selected_configuration[key]
        3) self[key]
        d) default

        Args:
            key (str): key to values from the respective dictionaries
            channel_modification (dict or :class:`.ObsMetadata`): modifications
                specified at station level
            selected_configuration (dict or :class:`.ObsMetadata`):
                component-level configuration
            default (dict or :class:`.ObsMetadata`): default value
        Returns:
            value (:class:`.ObsMetadata`): the highest priority value for 'key'            
        """
        key_found = False
        # If no original value, use default step (c)
        # WCC modified to give error message
        # if key in self:
        #     value = self[key]
        #     key_found=True
        #     logger.info(f'key "{key}" found in dict')
        # else:
        #     value = default
        value = self.get(key, default)

        if isinstance(selected_configuration, (dict, ObsMetadata)):
            # if key in selected_configuration:
            #     value = selected_configuration[key]
            #     logger.info(f'key "{key}" found in selected configuration')
            value = selected_configuration.get(key, value)

        if isinstance(channel_modification, (dict, ObsMetadata)):
            # if key in channel_modification:
            #     val = channel_modification[key]
            #     logger.info(f'key "{key}" found in channel_modification')
            # else:
            #     val = value
            val = channel_modification.get(key, value)
            # Do not assign value if this is a dictionary, so it's not a leaf
            # in the hierarchy
            if not isinstance(val, (dict, ObsMetadata)):
                value = val

        # if key_found is not True:
        #     logger.info(f'key "{key}" not found')

        if isinstance(value, dict):  # Convert any dict to ObsMetadata
            value = ObsMetadata(value)

        return value

    def validate_dates(dates):
        """
        Converts dates to a standard format

        Args:
            dates (list): dates as strings
        Returns:
            (list): formatted dates as strings
        """

        if dates is None or not isinstance(dates, list):
            return []

        return [ObsMetadata.validate_date(dt) for dt in dates]

    def validate_date(date):
        """
        Reformats an individual date

        Uses regular expressions to match known dates, either in UTC date
        format, in UTC date and time format or in regular dd-mm-yyyy format.
        If only two digits of year specified, assumes 21st century.
        The separator can be either "/" or "-"

        Args:
            date (str): a date in a given format
        Returns:
            (str): a reformatted date as string or None if no value
        Raises:
            (ValueError) if date is unrecognizable
        """

        if date is None or date == int(0):
            # 0 is sometimes the default, the epoch date, 1/1/1970
            return None

        regexp_date_UTC = re.compile("^[0-9]{4}[\-\/][0-1]{0,1}[0-9][\-\/][0-3]{0,1}[0-9]")
        regexp_date_and_time_UTC = re.compile("^[0-9]{4}[\-\/][0-1]{0,1}[0-9][\-\/][0-3]{0,1}[0-9]T[0-2][0-9]:[0-6][0-9]:{0,1}[0-6]{0,1}[0-9]{0,1}Z{0,1}")
        if (re.match(regexp_date_UTC, date) or re.match(regexp_date_and_time_UTC, date)):
            return date
        else:  # Assume it's a regular date
            warnings.warn(f'Date {date} is not UTC format, assuming regular '
                          'dd/mm/yyyy format')
            regexp_date_normal = re.compile("[\-\/]")
            date_elements = re.split(regexp_date_normal, date)
            if len(date_elements) != 3:
                raise ValueError("Unrecognizable date, must either be UTC or "
                                 "dd/mm/yyyy or dd/mm/yy. Dashes can be used "
                                 "as separators")
            if len(date_elements[2]) == 2:
                date_elements[2] = "20" + date_elements[2]
                warnings.warn(f'Date {date} is two digits, assuming 21st century')

            return f'{date_elements[2]}-{date_elements[1]}-{date_elements[0]}'
