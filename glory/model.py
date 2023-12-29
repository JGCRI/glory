"""
@Date: 11/2023
@author: Mengqi Zhao (mengqi.zhao@pnnl.gov)
@Project: GLORY v1.0

License:  BSD 2-Clause, see LICENSE and DISCLAIMER files
Copyright (c) 2023, Battelle Memorial Institute

"""

import logging
import os

from glory.data.read_config import ConfigReader
from glory.data.read_data import DataLoader
from glory.data.write_outputs import write_outputs
from glory.method.supply_curve import SupplyCurve
from glory.utils.diagnostics import diagnostics
from glory.utils.logger import init_logger
from glory.utils.cleanup import cleanup


class Glory:
    """ Model wrapper for pytemplate"""

    def __init__(self, config_file=None):

        # Read in Config File
        self.config = ConfigReader(config_file)

        init_logger(path=self.config.output_folder)

        logging.info('Starting GLORY model.')

        for period in self.config.scales['gcam_period']:

            # Read data
            self.data = DataLoader(config=self.config,
                                   period=period,
                                   base_period=self.config.scales['base_period'],
                                   demand_gcam=None,
                                   capacity_gcam=None)

            # Run main method
            self.outputs = SupplyCurve(config=self.config,
                                       period=period,
                                       demand_gcam=None,
                                       capacity_gcam=None)

            # Run diagnostics
            diagnostics(config=self.config, outputs=self.outputs, fig_path=os.path.join(self.config.output_folder, 'diagnostics'))

            # Write outputs
            write_outputs(config=self.config, outputs=self.outputs)

        # clean up and close
        cleanup()

def run_model(config_file):
    """Run GLORY model"""

    result = Glory(config_file=config_file)

    return result