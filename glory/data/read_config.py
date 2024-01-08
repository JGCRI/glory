"""
Module to load configuration data.

@author: Mengqi Zhao (mengqi.zhao@pnnl.gov)

@Project: GLORY v1.0

License:  BSD 2-Clause, see LICENSE and DISCLAIMER files

Copyright (c) 2023, Battelle Memorial Institute

"""

import os
import yaml
import logging

import glory


class ConfigReader:
    """
    Read config file
    """

    def __init__(self, config_file=None):

        # Initialization
        self.root = None
        self.output_folder = None

        # read all the keys
        if config_file is not None:
            config = self.read_config(config_file)
            config = {k: v for k, v in config.items()}
            vars(self).update(config)

        # root directory
        if self.root is None:
            if config_file is not None:
                self.root = os.path.dirname(config_file)
            else:
                self.root = glory.default_download_dir
        else:
            if (not os.path.exists(self.root)) and (os.path.exists(glory.default_download_dir)):
                logging.warning(f'The root directory provided: {self.root} is not a valid directory. '
                                f'Modified the root directory to the default download directory: {glory.default_download_dir}.')
                self.root = glory.default_download_dir
            else:
                raise FileExistsError(f'The root directory provided: glory/example is not a valid directory. '
                                      f'Please provide valid root directory.')

        # input files
        if self.input_files is not None:
            self.input_files = {k: os.path.join(self.root, v) for k, v in self.input_files.items()}

        # reference files
        if self.reference_files is not None:
            self.reference_files = {k: os.path.join(self.root, v) for k, v in self.reference_files.items()}

        # scales
        if self.scales is not None:
            self.scales = {k: v for k, v in self.scales.items()}

        # parameters
        if self.parameters is not None:
            self.parameters = {k: v for k, v in self.parameters.items()}

        # linear programming model
        if self.lp is not None:
            self.lp = {k: v for k, v in self.lp.items()}

        # outputs options
        if self.outputs is not None:
            self.outputs = {k: v for k, v in self.outputs.items()}
            self.output_folder = self.create_dir(os.path.join(self.root, self.outputs['output_folder']))


    @staticmethod
    def read_config(config_file=None):
        """
        Load configuration file.

        :param config_file:         configuration file path
        :type config_file:          string
        :return:
        """

        logging.info('Starting function read_config...')

        path_to_config = os.path.abspath(config_file)
        file_exists = os.path.exists(path_to_config)

        if not file_exists:
            raise FileNotFoundError(f'Config file provided: {path_to_config} does not exist.')

        if not path_to_config.endswith('.yml' or '.yaml'):
            raise TypeError(f'Config file provided: {path_to_config} is not a valid file.')

        with open(path_to_config, "r") as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise yaml.YAMLError(exc)

        logging.info('Function read_config completed successfully.')

        return config

    @staticmethod
    def create_dir(pth):
        """Check to see if the target path exists and create directory."""
        if os.path.isdir(pth) is False:
            os.mkdir(pth)
        return pth
