import os
import logging
import datetime


def custom_logger(name):
    """
    Return logging.logger with pre-defined format
    :param name: Logger module name
    :return: logging.logger
    """
    # /logs folder
    path_of_logs = os.path.dirname(os.path.realpath(__file__)) + "/../logs/"
    if not os.path.exists(path_of_logs):
        os.makedirs(path_of_logs)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(path_of_logs + '/{}.log'.format(datetime.datetime.now().strftime('%Y-%m-%d')))
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s [%(asctime)s] <%(name)s> %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger

