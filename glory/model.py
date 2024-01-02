"""
Model interface for GLORY.

@author: Mengqi Zhao (mengqi.zhao@pnnl.gov)

@Project: GLORY v1.0

License:  BSD 2-Clause, see LICENSE and DISCLAIMER files

Copyright (c) 2023, Battelle Memorial Institute

"""

import logging
import os
import time
import multiprocessing
from itertools import repeat

from glory.data.read_config import ConfigReader
from glory.data.read_data import DataLoader
from glory.data.write_outputs import write_outputs
from glory.method.supply_curve import SupplyCurve
from glory.utils.diagnostics import diagnostics
from glory.utils.logger import init_logger
from glory.utils.cleanup import cleanup


def execute(config, basin_id, period):
    """Execute"""

    print(f'Processing basin {basin_id} for the period {period}')
    # Run main method
    outputs = SupplyCurve(config=config,
                          basin_id=basin_id,
                          period=period,
                          demand_gcam=None,
                          capacity_gcam=None)

    # Run diagnostics for a single basin
    diagnostics(config=config, outputs=outputs,
                fig_path=os.path.join(config.output_folder, 'diagnostics'))

    return outputs


def run_model(config_file):
    """Run GLORY model"""

    # read configuration file
    config = ConfigReader(config_file)

    # get the selected periods and basins to run the model
    periods = config.scales['gcam_period']
    basin_ids = config.scales['basin_id']

    # apply all basin numbers if selected 'all'/'All'/'ALL'
    if isinstance(basin_ids[0], str) and ('all' in basin_ids.lower()):
        basin_ids = range(1, 236)

    # initialize
    init_logger(path=config.output_folder)

    logging.info('Starting GLORY model.')

    # loop through all selected periods
    for period in periods:

        # create a pool of processes based on the number of cores
        with multiprocessing.Pool() as pool:

            # document start time
            start_time = time.perf_counter()

            # run basins in parallel
            result = pool.starmap(execute, zip(repeat(config), basin_ids, repeat(period)))

            # close the process pool
            pool.close()

            # document finish time
            finish_time = time.perf_counter()

        # Write outputs for all basins
        write_outputs(config=config, outputs=result)

        # print logging info
        logging.info(f"Glory process completed in {round((finish_time - start_time), 2)} seconds for the period {period}.")

    # cleaning up
    cleanup()

