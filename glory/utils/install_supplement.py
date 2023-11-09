import os
import zipfile
import requests
import importlib.resources
import importlib.metadata
import logging
from io import BytesIO as BytesIO

default_download_dir = str(importlib.resources.files('glory'))


class InstallSupplement:
    """Download and unpack example data supplement from Zenodo that matches the current installed
    GLORY distribution.

    :param example_data_directory:              Full path to the directory you wish to install
                                                the GLORY example data to.  Must be write-enabled
                                                for the user.
    """

    # URL for DOI minted example data hosted on Zenodo
    DATA_VERSION_URLS = {
        '1.0.0': 'https://zenodo.org/records/8436685/files/inputs_glory.zip?download=1'
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
        logging.info(f"Downloading example data for GLORY version {current_version}. This might take a few minutes.")
        r = requests.get(data_link)

        with zipfile.ZipFile(BytesIO(r.content)) as zipped:

            # extract each file in the zipped dir to the project
            for f in zipped.namelist():
                logging.ingo("Unzipped: {}".format(os.path.join(self.example_data_directory, f)))
                zipped.extract(f, self.example_data_directory)


def get_example_data(example_data_directory=None):
    """Download and unpack example data supplement from Zenodo that matches the current installed
    GLORY distribution.

    :param example_data_directory:              Full path to the directory you wish to install
                                                the GLORY example data to.  Must be write-enabled
                                                for the user.

    :type example_data_directory:               str

    """

    if example_data_directory is None:
        example_data_directory = default_download_dir  # GLORY package directory

    zen = InstallSupplement(example_data_directory)

    zen.fetch_zenodo()
