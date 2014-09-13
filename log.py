
# -*- encoding= utf-8 -*-

import logging
import logging.handlers
import os

LOG_LEVELS = {
    'NOTSET': logging.NOTSET,
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}


def config_logging( file_name, log_level, logs_dir ):
    '''
    @summary: config logging to write logs to local file
    @param file_name: name of log file
    @param log_level: log level
    '''

    if not logs_dir:
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    if os.path.exists(logs_dir) and os.path.isdir(logs_dir):
        pass
    else:
        os.makedirs(logs_dir)

    file_name = os.path.join(logs_dir, file_name)

    #set a logfile rotating function  
    rotatingFileHandler = logging.handlers.RotatingFileHandler( filename =file_name,
                                                      maxBytes = 1024 * 1024 * 100,
                                                      backupCount = 20 )
    formatter = logging.Formatter("%(asctime)s %(name)-12s %(lineno)3d %(levelname)-8s %(message)s")
    rotatingFileHandler.setFormatter(formatter)
    logging.getLogger("").addHandler(rotatingFileHandler)

    # define a handler whitch writes messages to sys
    console = logging.StreamHandler()

    # set a format which is simple for console use
    formatter = logging.Formatter("%(name)-12s: %(lineno)d %(levelname)-8s %(message)s")

    # tell the handler to use this format
    console.setFormatter(formatter)

    # add the handler to the root logger
    logging.getLogger("").addHandler(console)
    # set  log level

    logger = logging.getLogger("")
    level = LOG_LEVELS [ log_level.upper() ]
    logger.setLevel(level)


def test_log():
    LOGGER.info("hello")
    LOGGER.debug("this is a debug log")
    LOGGER.info("this  is info log")
    LOGGER.critical("this is  CRITICAL log")


if __name__ == '__main__':
    LOGGER = logging.getLogger(__name__)
    config_logging('hello.log', 'INFO', None)
    test_log()

