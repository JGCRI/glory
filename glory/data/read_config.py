import os
import yaml
import logging

class ConfigReader:
    """
    Read config file
    """

    def __init__(self, config_file=None):

        # Initialization
        self.root = None
        self.output_folder = None

        if config_file is not None:
            config = self.read_config(config_file)
            config = {k: v for k, v in config.items()}
            vars(self).update(config)

        if self.root is None:
            if config_file is not None:
                self.root = os.path.dirname(config_file)
            else:
                self.root = os.getcwd()

        if self.input_files is not None:
            self.input_files = {k: os.path.join(self.root, v) for k, v in self.input_files.items()}

        if self.reference_files is not None:
            self.reference_files = {k: os.path.join(self.root, v) for k, v in self.reference_files.items()}

        if self.gcam is not None:
            self.gcam = {k: v for k, v in self.gcam.items()}

        if self.scales is not None:
            self.scales = {k: v for k, v in self.scales.items()}

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

        if file_exists:
            is_file = os.path.isfile(path_to_config)
            if is_file:
                with open(path_to_config, "r") as stream:
                    try:
                        config = yaml.safe_load(stream)
                    except yaml.YAMLError as exc:
                        print(exc)
            else:
                config = config_file
                logging.error(f'Config file provided: {path_to_config} is not a valid file.')
        else:
            config = config_file
            logging.error(f'Config file provided: {path_to_config} is not a valid file.')


        logging.info('Function read_config complete.')

        return config

    @staticmethod
    def create_dir(pth):
        """Check to see if the target path exists and create directory."""
        if os.path.isdir(pth) is False:
            os.mkdir(pth)
        return pth
