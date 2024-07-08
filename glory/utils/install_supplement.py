"""
Module to download example data.

@author: Mengqi Zhao (mengqi.zhao@pnnl.gov)

@Project: GLORY v1.0

License:  BSD 3-Clause, see LICENSE and DISCLAIMER files

Copyright (c) 2023, Battelle Memorial Institute

"""

import os
from pathlib import Path
import zipfile
import requests
import importlib.resources
import importlib.metadata
from io import BytesIO as BytesIO


DEFAULT_DOWNLOAD_DIR = Path(importlib.resources.files('glory-reservoir')).parent / 'example'


class InstallSupplement:
    """Download and unpack example data supplement from Zenodo that matches the current installed
    GLORY distribution.

    :param example_data_directory:              Full path to the directory you wish to install
                                                the GLORY example data to.  Must be write-enabled
                                                for the user.
    """

    # URL for DOI minted example data hosted on Zenodo
    DATA_VERSION_URLS = {
        '0.1.0': 'https://zenodo.org/records/10471982/files/example.zip?download=1',
    }

    def __init__(self, example_data_directory):

        # full path to the GLORY root directory where the example dir will be stored
        self.example_data_directory = example_data_directory

    def fetch_zenodo(self):
        """Download and unpack the Zenodo example data supplement for the
        current GLORY distribution."""

        # get the current version of GLORY that is installed
        current_version = importlib.metadata.version('glory')

        try:
            data_link = InstallSupplement.DATA_VERSION_URLS[current_version]

        except KeyError:
            msg = "Link to data missing for current version:  {}.  Please contact admin."
            raise(msg.format(current_version))

        # retrieve content from URL
        try:
            print(f"Downloading example data for GLORY version {current_version}. This might take a few minutes.")
            r = requests.get(data_link)
            r.raise_for_status()

        except requests.RequestException as err:
            raise f"An error occurred during the download: {err}"

        # unzipp file
        with zipfile.ZipFile(BytesIO(r.content)) as zipped:

            # extract each file in the zipped dir to the project
            for f in zipped.namelist():
                print("Unzipped: {}".format(os.path.join(self.example_data_directory, f)))
                zipped.extract(f, self.example_data_directory)

        print(f"Download completed.")


def get_example_data(example_data_directory=None):
    """Download and unpack example data supplement from Zenodo that matches the current installed
    GLORY distribution.

    :param example_data_directory:              Full path to the directory you wish to install
                                                the GLORY example data to.  Must be write-enabled
                                                for the user.

    :type example_data_directory:               str

    """

    # download to package folder by default
    if example_data_directory is None:
        example_data_directory = DEFAULT_DOWNLOAD_DIR  # GLORY package directory

    # if the 'example' folder already exists in the path, then skip the download
    if os.path.exists(example_data_directory) and os.listdir(example_data_directory):
        print(f"The directory at {example_data_directory} is not empty, "
              f"so download has been skipped. "
              f"To download data again, please delete existing folder or save to an alternative directory.")
    else:
        os.makedirs(example_data_directory, exist_ok=True)

        zen = InstallSupplement(example_data_directory)

        zen.fetch_zenodo()

