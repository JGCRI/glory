"""
Module to clean up the logging handler.

@author: Mengqi Zhao (mengqi.zhao@pnnl.gov)

@Project: GLORY v1.0

License:  BSD 2-Clause, see LICENSE and DISCLAIMER files

Copyright (c) 2023, Battelle Memorial Institute

"""

import logging


def cleanup():
    """Close log files."""

    logging.info('Cleaning up...')
    # Remove logging handlers - they are initialized at the module level, so this prevents duplicate logs from
    # being created if Xanthos is run multiple times.
    logger = logging.getLogger()
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    logging.info('GLORY model run finished.')
