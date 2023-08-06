"""
Write a script to convert LCHEAPO data to SDS* using the lcheapo** python package

Includes clock drift and leap-second correction
Script is a BASH shell script
*SDS = SeisComp Data Structure
**THIS PROGRAM DOES NOT CREATE DATA-CENTER QUALITY DATA:
    - drift correction is calculated for each day, not each record
    - does not set drift correction record header flags
    - does not fill in record header time_correction field
"""
import os.path
from pathlib import Path
import warnings

# import obsinfo
from obsinfo.network import Network
from ..misc.discoveryfiles import (Datapath)
from ..obsMetadata.obsmetadata import (ObsMetadata)
from .LCHEAPO import _get_ref_code

SEPARATOR_LINE = "\n# " + 60 * "=" + "\n"


def process_script(network_code, stations, station_data_path, input_dir=".",
                   output_dir="../", include_header=True, no_drift_correct=False):
    """
    Writes script to transform raw OBS data to SeisComp Data Structure

    Arguments:
        network_code (str): FDSN network_code
        stations (list of :class:`.Station`): the stations to process
        station_data_path (str): the base directory beneath the station data dirs
        input_dir (str): directory beneath station_dir for LCHEAPO data
        output_dir (str): directory beneath station_dir for SDS directory
        include_header (bool): include the header that sets up paths
                               (should be done once)
        no_drift_correct (bool): Do NOT drift correct
    """
    fixed_dir = "lcheapo_fixed"
    s = _header(station_data_path)
    s += _run_station_function(network_code, fixed_dir, output_dir)
    for station in stations:
        # station_dir = os.path.join(station_data_path, station.label)
        s += _run_station_call(station, no_drift_correct)
    return s


def _header(station_data_path):
    s = "#!/bin/bash\n\n"
    s += f'DATA_DIR={station_data_path}\n\n'
    return s


def _run_station_function(network_code, fixed_dir='lcheapo_fixed', output_dir="../"):
    s = ('run_station () {\n'
         '    # Run lcfix and lc2SDS_weak for one station\n'
         '    # $1: station name\n'
         '    # $2: obs type\n'
         '    # $3: reference start sync time\n'
         '    # $4: instrument start sync time [if empty, uses $3]\n'
         '    # $5: reference end sync time [if empty, do not shift times]\n'
         '    # $6: obs clock end sync time\n'
         '    # $7: leap-second times [empty if none]\n'
         '    # $8: leap-second types [empty if none]\n'
         '    echo "Working on station $1"\n'
         '    STATION_DIR=$DATA_DIR/$1\n'
         '    echo "------------------------------------------------------------"\n'
         '    echo "Running LCFIX"\n'
         f'    mkdir $STATION_DIR/{fixed_dir}\n'
         '    command cd $STATION_DIR\n'
         '    lchfiles=$(command ls *.lch)\n'
         '    command cd -\n'
         '    echo "lchfiles:" $lchfiles\n'
         f'    lcfix $lchfiles -d "$STATION_DIR" -o "{fixed_dir}"\n'
         '    echo "------------------------------------------------------------"\n'
         '    echo "Running LC2SDS_weak"\n'
         f'    mkdir -p $STATION_DIR/{output_dir}\n'
         f'    command cd $STATION_DIR/{fixed_dir}\n'
         '    lchfiles=$(command ls *.fix.lch)\n'
         '    command cd -\n'
         '    echo "lchfiles:" $lchfiles\n'
         '    if [ -z "$7" ]\n'
         '    then  # NO LEAP-SECOND INFORMATION\n'
         '        if [ -z "$5" ]\n'
         '        then  # NO END SYNC, DO NOT SHIFT TIMES\n'
         f'            cmd="lc2SDS_weak $lchfiles -d \\"$STATION_DIR\\" -i \\"{fixed_dir}\\" -o \\"{output_dir}\\" --network \\"{network_code}\\" --station \\"$1\\" --obs_type \\"$2\\""\n'
         '        elif [ -z "$4" ]\n'
         '        then  # NO INSTRUMENT START SYNC, ASSUME SAME AS REFERENCE\n'
         f'            cmd="lc2SDS_weak $lchfiles -d \\"$STATION_DIR\\" -i \\"{fixed_dir}\\" -o \\"{output_dir}\\" --network \\"{network_code}\\" --station \\"$1\\" --obs_type \\"$2\\" --start_times \\"$3\\" --end_times \\"$5\\" \\"$6\\""\n'
         '        else  # INSTRUMENT START SYNC SUPPLIED\n'
         f'            cmd="lc2SDS_weak $lchfiles -d \\"$STATION_DIR\\" -i \\"{fixed_dir}\\" -o \\"{output_dir}\\" --network \\"{network_code}\\" --station \\"$1\\" --obs_type \\"$2\\" --start_times \\"$3\\" \\"$4\\" --end_times \\"$5\\" \\"$6\\""\n'
         '        fi\n'
         '    else  # THERE IS LEAP-SECOND INFORMATION\n'
         '        if [ -z "$5" ]\n'
         '        then\n'
         f'            cmd="lc2SDS_weak $lchfiles -d \\"$STATION_DIR\\" -i \\"{fixed_dir}\\" -o \\"{output_dir}\\" --network \\"{network_code}\\" --station \\"$1\\" --obs_type \\"$2\\" --leapsecond_times \\"$7\\" --leapsecond_types \\"$8\\""\n'
         '        elif [ -z "$4" ]\n'
         '        then\n'
         f'            cmd="lc2SDS_weak $lchfiles -d \\"$STATION_DIR\\" -i \\"{fixed_dir}\\" -o \\"{output_dir}\\" --network \\"{network_code}\\" --station \\"$1\\" --obs_type \\"$2\\" --start_times \\"$3\\" --end_times \\"$5\\" \\"$6\\" --leapsecond_times \\"$7\\" --leapsecond_types \\"$8\\""\n'
         '        else\n'
         f'            cmd="lc2SDS_weak $lchfiles -d \\"$STATION_DIR\\" -i \\"{fixed_dir}\\" -o \\"{output_dir}\\" --network \\"{network_code}\\" --station \\"$1\\" --obs_type \\"$2\\" --start_times \\"$3\\" \\"$4\\" --end_times \\"$5\\" \\"$6\\" --leapsecond_times \\"$7\\" --leapsecond_types \\"$8\\""\n'
         '        fi\n'
         '    fi\n'
         '    echo "Running: $cmd"\n'
         '    eval $cmd\n'
         '    echo "------------------------------------------------------------"\n'
         '    echo "Removing intermediate files"\n'
         f'    command rm -r $STATION_DIR/{fixed_dir}\n'
         '}\n\n')
    return s


def _run_station_call(station, no_drift_correct):

    """
    Write a call to the run_station() function

    Args:
        station (:class:`.Station`): station information
        no_drift_correct (bool): do NOT drift correct
    Returns:
        s (str): single-line call
    """
    station_code = station.label
    obs_type = _get_ref_code(station.instrumentation)
    leaptimes, leaptypes = [], []
    ccld = None
    start_sync_ref, start_sync_inst, end_sync_ref, end_sync_inst = "", "", "", ""
    leaptimes_str, leaptypes_str = "", ""
    for proc in station.processing.attributes:
        if 'clock_correction_linear' in proc:
            if ccld is not None:
                warnings.warn('more than one linear clock_correction_linear, '
                              'only applying first')
            else:
                ccld = proc['clock_correction_linear']
        elif 'clock_correction_leapsecond' in proc:
            leaptimes.append(proc['clock_correction_leapsecond']['time'])
            leaptypes.append(proc['clock_correction_leapsecond']['type'])
    if ccld is not None:
        start_sync_ref = ccld["start_sync_reference"]
        start_sync_inst = ccld.get("start_sync_instrument", "")
        if start_sync_inst == 0:
            start_sync_inst = ""
        end_sync_ref = ccld["end_sync_reference"]
        end_sync_inst = ccld["end_sync_instrument"]
    if leaptimes:
        raise ValueError("the network file provides leapseconds: run_station can't (yet) handle that")
        leaptimes_str = " ".join(leaptimes)
        leaptypes_str = " ".join(leaptypes)
    s = f'run_station "{station_code}" "{obs_type}" '
    if no_drift_correct is True:
        s += '"" "" "" "" '
    else:
        s += f'"{start_sync_ref}" "{start_sync_inst}" "{end_sync_ref}" "{end_sync_inst}" '
    s += f'"{leaptimes_str}" "{leaptypes_str}"\n'

    return s


def _console_script(argv=None):
    """
    Create a bash-script to convert LCHEAPO data to SDS, with time correction
    """
    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    parser = ArgumentParser(prog="obsinfo-makescripts_LS2SDS",
                            description=__doc__,
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("network_file", help="Network information file")
    parser.add_argument("station_data_path",
                        help="Base path containing the station directories")
    parser.add_argument("-i", "--input_dir", default=".",
                        help="subdirectory of station_data_path/{STATION}/ "
                             "containing input *.lch files "
                             "(default: %(default)s)")
    parser.add_argument("-o", "--output_dir", default="../",
                        help="subdirectory of station_data_path/{STATION}/ "
                             "to put output SDS directory "
                             "(default: %(default)s)")
    parser.add_argument("--suffix", default="_LC2SDS",
                        help="suffix for script filename "
                             "(default: %(default)s)")
    # parser.add_argument("--append", action="store_true",
    #                     help="append to existing script file")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")
    parser.add_argument("--no_header", action="store_true",
                        help="do not include a script header")
    parser.add_argument("--no_drift_correct", action="store_true",
                        help="do not correct for instrument drift")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="run silently")
    args = parser.parse_args()

    if not args.quiet:
        print("Creating LC2SDS_weak process script, ", end="", flush=True)

    # READ IN NETWORK INFORMATION
    dp = Datapath()
    if args.verbose:
        print(f'Reading network file: {args.network_file}')
    args.network_file = str(Path(os.getcwd()).joinpath(args.network_file))
    info_dict = ObsMetadata.read_info_file(args.network_file, dp, False)
    net_dict = info_dict.get('network', None)
    if not net_dict:
        return
    if args.verbose:
        print(f'Processing network file: {args.network_file}')
    network = Network(ObsMetadata(net_dict))
    # network = oi_Network(args.network_file)

    if not args.quiet:
        print(f"network {network.fdsn_code}, stations ", end="", flush=True)
        if args.verbose:
            print("")

    # scripts = []
    # first_time = True
    script = process_script(network.fdsn_code,
                            network.stations,
                            args.station_data_path,
                            input_dir=args.input_dir,
                            output_dir=args.output_dir,
                            no_drift_correct=args.no_drift_correct)
    if not args.quiet:
        print(', '.join([s.label for s in network.stations]))
    if args.no_drift_correct is True:
        args.suffix += '_NODRIFTCORRECT'
    fname = "process" + args.suffix + ".sh"
    if args.verbose:
        print(f" ... writing file {fname}", flush=True)
    with open(fname, 'w') as f:
        f.write(script)
        f.close()
    if not args.verbose and not args.quiet:
        print("")
