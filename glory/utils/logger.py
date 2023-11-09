import logging
import os
import sys
import datetime

def init_logger(path):
    """
    Initialize project-wide looger.
    """

    log_format = logging.Formatter('%(levelname)s - %(message)s')
    log_level = logging.INFO
    log_file = os.path.join(path, 'logfile.log')

    logger = logging.getLogger()
    logger.setLevel(log_level)

    # logger file handler
    f_handler = logging.FileHandler(log_file, mode='w')
    f_handler.setLevel(log_level)
    f_handler.setFormatter(log_format)
    logger.addHandler(f_handler)


    # logger console handler
    # c_handler = logging.StreamHandler()
    # c_handler.setLevel(log_level)
    # c_handler.setFormatter(log_format)
    # logger.addHandler(c_handler)


    logging.info('logging started at: %s', datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
