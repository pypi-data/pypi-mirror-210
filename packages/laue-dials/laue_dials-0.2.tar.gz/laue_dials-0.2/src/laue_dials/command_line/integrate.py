#!/usr/bin/env python
"""
This script generates integrated MTZ files from refined data with predictions
"""
import logging
from functools import partial
from itertools import repeat
from multiprocessing import Pool

import gemmi
import libtbx.phil
import numpy as np
import reciprocalspaceship as rs
from cctbx import sgtbx
from dials.array_family import flex
from dials.util import log, show_mail_handle_errors
from dials.util.options import (ArgumentParser,
                                reflections_and_experiments_from_files)

from laue_dials.algorithms.integration import SegmentedImage

logger = logging.getLogger("laue-dials.command_line.integrate")

help_message = """

This program takes a refined geometry experiment file along with a predicted
reflection table, and uses those to integrate intensities in the data set.

The output is a MTZ file containing integrated intensities suitable for
merging and scaling.

Examples::

    laue.integrate [options] poly_refined.expt predicted.refl
"""

# Set the phil scope
phil_scope = libtbx.phil.parse(
    """
output {
  filename = 'integrated.mtz'
    .type = str
    .help = "The output MTZ filename."

  log = 'laue.integrate.log'
    .type = str
    .help = "The log filename."
  }

n_proc = 1
  .type = int
  .help = Number of parallel integrations to do
""",
    process_includes=True,
)

working_phil = phil_scope.fetch(sources=[phil_scope])


def get_refls_image(refls, img_id):
    """
    A function for getting the set of reflections lying on a particular image
    """
    return refls.select(refls["id"] == img_id)


def integrate_image(params, img_set, refls):
    """
    A function for integrating predicted spots on an image
    """
    isigi_cutoff = 2.0  # i/sigma cutoff for strong spot profiles

    # Make SegmentedImage
    all_spots = refls["xyzcal.px"].as_numpy_array()[:, :2].astype("float32")
    pixels = img_set.get_raw_data(0)[0].as_numpy_array().astype("float32")
    sim = SegmentedImage(pixels, all_spots)

    # Get integrated reflections only
    refls = refls.select(flex.bool(sim.used_reflections))

    # Integrate reflections
    sim.integrate(isigi_cutoff)

    # Update reflection data
    i = np.zeros(len(refls))
    sigi = np.zeros(len(refls))
    bg = np.zeros(len(refls))
    sigbg = np.zeros(len(refls))
    profiles = sim.profiles.to_list()
    for j in range(len(refls)):
        prof = profiles[j]
        if prof.success:
            i[j] = prof.I
            sigi[j] = prof.SigI
            bg[j] = np.maximum((prof.background * prof.bg_mask), 0.0).sum()
            sigbg[j] = np.sqrt(np.maximum((prof.background * prof.bg_mask), 0.0)).sum()
    refls["intensity.sum.value"] = flex.double(i)
    refls["intensity.sum.variance"] = flex.double(sigi**2)
    refls["background.sum.value"] = flex.double(bg)
    refls["background.sum.variance"] = flex.double(sigbg**2)
    refls = refls.select(refls["intensity.sum.value"] != 0)
    return refls  # Updated reflection table


@show_mail_handle_errors()
def run(args=None, *, phil=working_phil):
    # Parse arguments
    usage = "laue.integrate [options] poly_refined.expt predicted.refl"

    parser = ArgumentParser(
        usage=usage,
        phil=phil,
        read_reflections=True,
        read_experiments=True,
        check_format=True,
        epilog=help_message,
    )

    params, options = parser.parse_args(args=args, show_diff_phil=True)

    # Configure logging
    log.config(verbosity=options.verbose, logfile=params.output.log)

    # Log diff phil
    diff_phil = parser.diff_phil.as_str()
    if diff_phil != "":
        logger.info("The following parameters have been modified:\n")
        logger.info(diff_phil)

    # Load data
    reflections, expts = reflections_and_experiments_from_files(
        params.input.reflections, params.input.experiments
    )
    preds = reflections[0]  # Get predictions

    # Sanity checks
    if len(expts) == 0:
        parser.print_help()
        return

    # Get reflections and image data
    imagesets = expts.imagesets()
    ids = list(np.unique(preds["id"]).astype(np.int32))
    get_refls = partial(get_refls_image, preds)
    tables = list(map(get_refls, ids))
    inputs = list(zip(repeat(params), imagesets, tables))

    # Multiprocess integration
    num_processes = params.n_proc
    print("Starting integration")
    with Pool(processes=num_processes) as pool:
        refls_arr = pool.starmap(integrate_image, inputs)
    print("Integration finished.")

    # Construct an integrated reflection table
    final_refls = flex.reflection_table()
    for refls in refls_arr:
        final_refls.extend(refls)
    refls = final_refls

    # Get data needed for MTZ file
    hkl = refls["miller_index"].as_vec3_double()
    cell = np.zeros(6)
    for crystal in expts.crystals():
        cell += np.array(crystal.get_unit_cell().parameters()) / len(expts.crystals())
    cell = gemmi.UnitCell(*cell)
    sginfo = expts.crystals()[0].get_space_group().info()
    symbol = sgtbx.space_group_symbols(sginfo.symbol_and_number().split("(")[0])
    spacegroup = gemmi.SpaceGroup(symbol.universal_hermann_mauguin())

    # Generate rs.DataSet to write to MTZ
    data = rs.DataSet(
        {
            "H": hkl.as_numpy_array()[:, 0].astype(np.int32),
            "K": hkl.as_numpy_array()[:, 1].astype(np.int32),
            "L": hkl.as_numpy_array()[:, 2].astype(np.int32),
            "BATCH": refls["imageset_id"].as_numpy_array() + 1,
            "I": refls["intensity.sum.value"].as_numpy_array(),
            "SIGI": refls["intensity.sum.variance"].as_numpy_array() ** 0.5,
            "xcal": refls["xyzcal.px"].as_numpy_array()[:, 0],
            "ycal": refls["xyzcal.px"].as_numpy_array()[:, 1],
            "wavelength": refls["wavelength"].as_numpy_array(),
            "BG": refls["background.sum.value"].as_numpy_array(),
            "SIGBG": refls["background.sum.variance"].as_numpy_array() ** 0.5,
        },
        cell=cell,
        spacegroup=spacegroup,
    ).infer_mtz_dtypes()

    # Save reflections
    logger.info("Saving integrated reflections to %s", params.output.filename)
    data.write_mtz(params.output.filename, skip_problem_mtztypes=True)


if __name__ == "__main__":
    run()
