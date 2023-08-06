import argparse
import logging
import os
import re

import numpy as np
from tomoscan.framereducerbase import ReduceMethod

from nxtomomill.converter import from_h5_to_nx
from nxtomomill.io.config import TomoHDF5Config

from ..utils.flat_reducer import flat_reducer
from ..utils.utils import strip_extension

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def get_arguments(user_args):
    parser = argparse.ArgumentParser(
        description="""
        creates all the target nxs for all the stages.
        If the postfixes for reference scans are give (the one before and another after the measurements) the reduced flats dark are also created.
        The references scans are expected to contains projections to be 'interpreted' as flats
        """
    )
    parser.add_argument(
        "--filename_template",
        required=True,
        help="""The filename template. For zstage it must  contain one or more  segments equal to "X"*ndigits  which will be replaced by the stage number, for the scans, and, for the reference scans, by the begin/end prefixes""",
    )
    parser.add_argument(
        "--entry_name", required=False, help="entry_name", default="entry0000"
    )

    parser.add_argument(
        "--total_nstages",
        type=int,
        default=None,
        required=True,
        help="How many stages. Example: from 0 to 43 -> --total_nstages  44. ",
    )
    parser.add_argument(
        "--first_stage",
        type=int,
        default=0,
        required=False,
        help="Optional. Defaults to zero. The number of the first considered stage. Use this to do a smaller sequence",
    )
    parser.add_argument(
        "--last_stage",
        type=int,
        default=-1,
        required=False,
        help="Optional. Defaults to total_nstages-1. The number of the last considered stage. Use this to do a smaller sequence",
    )

    parser.add_argument(
        "--do_references",
        type=str2bool,
        default=False,
        required=False,
        help="Optional. If given the reference scans are used for the extraction of the flats/dark. The reference scans are obtained using the ref postfixes",
    )

    parser.add_argument(
        "--ref_scan_begin",
        type=str,
        default="REF_B_0000",
        required=False,
        help="""used when "do_reference" is True. It is optional. It is the postfix for the reference scan and defaults to REF_B_0000 """,
    )

    parser.add_argument(
        "--ref_scan_end",
        type=str,
        default="REF_E_0000",
        required=False,
        help="""used when "do_reference" is True. It is optional. It is the postfix for the reference scan and defaults to REF_E_0000 """,
    )

    parser.add_argument(
        "--target_directory",
        type=str,
        default="./",
        required=False,
        help="""Where files are written. Optional, defaults to current directory""",
    )
    parser.add_argument(
        "--median_or_mean",
        type=str,
        choices=[ReduceMethod.MEAN.value, ReduceMethod.MEDIAN.value],
        default=ReduceMethod.MEAN.value,
        required=False,
        help="""Choose betwen median or mean. Optional. Default is mean""",
    )

    args = parser.parse_args(user_args)

    if args.last_stage == -1:
        args.last_stage = args.total_nstages - 1

    return args


def _convert_bliss2nx(bliss_ref_name, nexus_name):
    config = TomoHDF5Config()
    config.input_file = bliss_ref_name
    config.output_file = nexus_name
    from_h5_to_nx(config)


def main(argv):
    args = get_arguments(argv[1:])

    pattern = re.compile("[X]+")
    # X represent the variable part of the 'template'
    # for example if we want to treat scans HA_2000_sample_0000.nx, ..., HA_2000_sample_9999.nx then
    # we expect the template to be HA_2000_sample_XXXX.nx
    # warning: If the dataset base names contains several X substrings the longest ones will be taken.
    ps = pattern.findall(args.filename_template)
    ls = list(map(len, ps))
    idx = np.argmax(ls)
    if len(ps[idx]) < 2:
        message = f""" The argument filename_template should contain  one or more substrings  formed by at least two 'X'
        The filename_template was {args.filename_template}
        """
        raise ValueError(message)
    name_template_for_numeric = args.filename_template.replace(
        ps[idx], "{i_stage:" + "0" + str(ls[idx]) + "d}"
    )

    if args.do_references:
        refs_nexus_names = []
        for bliss_ref_name in (args.ref_scan_begin, args.ref_scan_end):
            nexus_name = os.path.join(
                args.target_directory,
                strip_extension(os.path.basename(bliss_ref_name), _logger) + ".nx",
            )

            _convert_bliss2nx(bliss_ref_name, nexus_name)

            refs_nexus_names.append(nexus_name)

    for iz in range(args.first_stage, args.last_stage + 1):
        bliss_name = name_template_for_numeric.format(i_stage=iz)
        nexus_name = os.path.join(
            args.target_directory,
            strip_extension(os.path.basename(bliss_name), _logger) + ".nx",
        )

        _convert_bliss2nx(bliss_name, nexus_name)

        if args.do_references:
            factor = (iz + 1) / (args.total_nstages)
            flat_reducer(
                nexus_name,
                ref_start_filename=refs_nexus_names[0],
                ref_end_filename=refs_nexus_names[1],
                mixing_factor=factor,
                entry_name=args.entry_name,
                median_or_mean=args.median_or_mean,
                save_intermediated=False,
                reuse_intermediated=True,
            )
    return 0
