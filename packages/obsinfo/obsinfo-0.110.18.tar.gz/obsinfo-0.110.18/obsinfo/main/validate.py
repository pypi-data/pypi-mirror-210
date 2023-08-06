#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
     Main functions for obsinfo-validate.

     obsinfo strongly follows the hierarchy of StationXML files.

     Module contains both class ValidateObsinfo and a main entry point for obsinfo-validate
"""
import os
from pathlib import Path
import glob
import difflib
import re
import sys
from argparse import ArgumentParser
import logging
from logging.handlers import RotatingFileHandler

from obsinfo.misc.discoveryfiles import Datapath
import obsinfo
from obsinfo.obsMetadata.obsmetadata import ObsMetadata
from obsinfo.misc.const import EXIT_SUCCESS


class ValidateObsinfo():
    """
    Contains methods to validate each level of information files.

    Attributes:
        datapath (:class:`/.Datapath`): Store datapath list(s)
        verbose (bool): Prints progress messages
        remote (bool): Indicates file in command line argument is to be found
            using datapath
        debug (bool): Print more detailed messages.
    """

    def setUp(self, verbose=True, remote=False, debug=False):
        """
        Set up status variables according to .obsinforc and command line arguments.

        Args:
            verbose (bool): Print several progress messages
            remote (bool): Find file in command line argument using datapath
            debug (bool): Print more detailed messages and enable traceback
                of exceptions
        Returns: self
        """
        dp = Datapath()
        self.datapath = dp
        self.datapath.infofiles_path = dp.datapath_list
        self.datapath.validate_path = Path(obsinfo.__file__).parent.joinpath('data', 'schemas')

        self.verbose = verbose
        self.remote = remote
        self.debug = debug

        return self

    def assertTextFilesEqual(self, first, second, msg=None):
        """
        Compares two text files

        Args:
            first (str): First file to compare
            second (str): Second file to compare
            msg (str): Message to print in case of failure
        """
        with open(first) as f:
            str_a = f.read()
        with open(second) as f:
            str_b = f.read()
        if str_a != str_b:
            first_lines = str_a.splitlines(True)
            second_lines = str_b.splitlines(True)
            delta = difflib.unified_diff(
                first_lines, second_lines,
                fromfile=first, tofile=second)
            message = ''.join(delta)
            if msg:
                message += " : " + msg
            self.fail("Multi-line strings are unequal:\n" + message)

    def validate_filters_in_directory(self, dir):
        """
        Validate all information files in filter directory.

        Args:
            dir (str): directory where filter files reside
        """
        if dir.is_dir():
            for file in dir.iterdir():
                self.validate_single_file(file, "filter")

    def validate_stages_in_directory(self, dir):
        """
        Validate all information files in stage directory as given by datapath.

        Args:
            1dir (str): directory where stage files reside
        """
        datalogger_dir_re = re.compile(".*/dataloggers")
        sensor_dir_re = re.compile(".*/sensors")
        exception_re = re.compile(".*/test-with")
        if re.match(datalogger_dir_re, str(dir)) or re.match(sensor_dir_re, str(dir)):
            for file in (Path(dir).joinpath("responses")).iterdir():
                if not file.is_dir() and re.match(exception_re, str(file)) is None:
                    self.validate_single_file(file, "stage")

    def validate_single_file(self, info_file, filetype):
        """
        Validate a single obsinfo file.

        Args:
            info_file (str): info file to validate. No assumptions made about
                path.
            filetype (str): the information file type
        Returns:
            (bool): True if validated, False if not
        """
        try:
            ret = ObsMetadata().validate(self.datapath.validate_path,
                                         info_file,
                                         self.remote, "yaml",
                                         filetype,
                                         self.verbose,
                                         filetype + '.schema.json',
                                         False)
        except Exception as e:
            print(str(e))
            return False
        if self.verbose:
            self._print_passed(f'{filetype} test for: {info_file}', ret)
        return ret

    def validate_all_components(self):
        """
        Validate all information files in each components (sensor, preamplifier, datalogger) subdirectory
        as given by datapath
        """
        components_list = ("sensors", "preamplifiers", "dataloggers")
        for dir in self.datapath.infofiles_path:
            for comp in components_list:
                # includes sensors, preamplifiers and dataloggers
                files_in_validate_dir = Path(dir).joinpath(comp, "*.yaml")
                self.validate_files(files_in_validate_dir, comp)

    def validate_all_filters(self):
        """
        Validate all filter files in datapath/<component>/responses/filters/"
        """
        for dir in self.datapath.infofiles_path:
            # "*rs includes sensors, preamplifiers and dataloggers"
            files_in_validate_dir = Path(dir).joinpath("*rs", "responses",
                                                       "filters", "*.yaml")
            self.validate_files(files_in_validate_dir, "filter")

    def validate_all_stages(self):
        """
        Validate all stage files in datapath/<component>/responses/
        """
        for dir in self.datapath.infofiles_path:
            # "*rs includes sensors, preamplifiers and dataloggers"
            files_in_validate_dir = Path(dir).joinpath("*rs", "responses",
                                                       "*.yaml")
            self.validate_files(files_in_validate_dir, "stage")

    def validate_all_instrumentations(self):
        """
        Validate all instrumentation files in datapath/instrumentation/
        """
        for dir in self.datapath.infofiles_path:
            # includes sensors, preamplifiers and dataloggers
            files_in_validate_dir = Path(dir).joinpath("instrumentation/*.yaml")
            self.validate_files(files_in_validate_dir, "instrumentation")

    def validate_all_networks(self):
        """
        Validate all network files in datapath/network/
        """
        for dir in self.datapath.infofiles_path:
            # includes sensors, preamplifiers and dataloggers
            files_in_validate_dir = Path(dir).joinpath("network/*.yaml")
            self.validate_files(files_in_validate_dir, "network")

    def validate_files(self, files, filetype):
        """
        Validate all files of a given type

        Args:
            files (:class:`Path`): Full paths of files (including wildcards)
            filetype (str): information file type
        """
        assert ObsMetadata.is_valid_type(filetype)

        filelist = glob.glob(str(files))
        for file in filelist:
            self.validate_single_file(file, filetype)

    @staticmethod
    def _print_passed(text, passed):
        if passed:
            print(f'{text}: PASSED')
        else:
            print(f'{text}: FAILED')


def main():
    """
    Entry point for obsinfo-validate.

     1) Setups status variables from command line arguments.
     2) Validates file according to file type contained in name
     3) Manages all uncaught exceptions
    """
    args = retrieve_arguments()
    input_filename = args.input_filename
    logger = init_logging()

    val = ValidateObsinfo()
    val.setUp(verbose=args.verbose, remote=args.remote, debug=args.debug)

    if args.schema:
        if ObsMetadata.is_valid_type(args.schema):
            filetype = args.schema
        else:
            raise ValueError(f'Unknown schema type: {args.schema}')
    else:
        filetype = ObsMetadata.get_information_file_type(input_filename)

    if args.verbose:
        print(f'Validating {filetype} file')

#     try:
    val.validate_single_file(input_filename, filetype)

#     except TypeError as e:
#         print("TypeError:" + str(e))
#         logger.error("TypeError: Illegal format: fields may be missing or with wrong format in input file, or there is a programming error")
#         if args.debug:
#             raise
#         sys.exit(EXIT_DATAERR)
#     except (KeyError, IndexError) as e:
#         print("Illegal value in dictionary key or list index:" + str(e))
#         logger.error("KeyError, IndexError: Illegal value in dictionary key or list index")
#         if args.debug:
#             raise
#         sys.exit(EXIT_SOFTWARE)
#     except ValueError as e:
#         print("ValueError:" + str(e))
#         logger.error("ValueError: An illegal value was detected")
#         if args.debug:
#             raise
#         sys.exit(EXIT_DATAERR)
#     except FileNotFoundError as e:
#         if args.debug:
#             raise
#         print("File not found:" + str(e))
#         logger.error(f"FileNotFoundError: {str(e)}")
#         sys.exit(EXIT_NOINPUT)
#     except JSONDecodeError as e:
#         print("JSONDecodeError:" + str(e))
#         logger.error("JSONDecodeError: File and/or subfiles have an illegal format. Probably indentation or missing quotes/parentheses/brackets")
#         if args.debug:
#             raise
#         sys.exit(EXIT_DATAERR)
#     except (IOError, OSError, LookupError) as e:
#         print("File could not be opened or read:" + str(e))
#         logger.error("IOError, OSError, LookupError: File could not be opened or read")
#         if args.debug:
#             raise
#         sys.exit(EXIT_UNAVAILABLE)
#     except AttributeError as e:
#         print("Attribute error: " + str(e))
#         logger.debug("AttributeError: Programming error: an object in code had a wrong attribute")
#         if args.debug:
#             raise
#         sys.exit(EXIT_SOFTWARE)
#     except:
#         print("General exception")
#         logger.debug("General exception:")
#         if args.debug:
#             raise
#         sys.exit(EXIT_FAILURE)
#
    sys.exit(EXIT_SUCCESS)


def retrieve_arguments():
    """
    Retrieve arguments from command line. Setup several status variables and get information file name

    :returns: dictionary object with all status variables and information file name.
    """
    # Parse the arguments
    parser_args = ArgumentParser(prog="obsinfo-validate")

    # flags
    parser_args.add_argument(
        "-q", "--quiet", action='store_true', default=False,
        help="Quiet operation. Don't print informative messages")
    parser_args.add_argument(
        "-s", "--schema", help="Force validation against given schema")
    parser_args.add_argument(
        "-r", "--remote", action='store_true', default=False,
        help="Search input_filename in the DATAPATH repositories")
    parser_args.add_argument(
        "-d", "--debug", action='store_true', default=False,
        help="Print traceback for exceptions")
    # positional arguments
    parser_args.add_argument("input_filename", type=str,
                             help="Information file to be validated.")

    args = parser_args.parse_args()
    args.verbose = not args.quiet

    if not Path(args.input_filename).is_absolute():
        args.input_filename = str(Path(os.getcwd()).joinpath(args.input_filename).resolve())
    return args


def init_logging():
    """
    Create or open a rotating logging file and add it to ObsinfoConfiguration

    :returns: object of Logger class
    """
    logfile = Path.home().joinpath('.obsinfo', 'obsinfolog-validate')

    logger = logging.getLogger("obsinfo")

    logger.setLevel(logging.DEBUG)
    # add a rotating handler with 200K (approx) files and just two files
    handler = RotatingFileHandler(logfile, maxBytes=200000,
                                  backupCount=2)
    frmt = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                             datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(frmt)
    logger.addHandler(handler)

    return logger


if __name__ == '__main__':
    main()
