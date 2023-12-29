import logging


def cleanup():
    """Close log files."""
    logging.info('GLORY model run complete.')

    # Remove logging handlers - they are initialized at the module level, so this prevents duplicate logs from
    # being created if Xanthos is run multiple times.
    logger = logging.getLogger()
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
