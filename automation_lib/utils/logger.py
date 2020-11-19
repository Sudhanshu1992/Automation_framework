import logging
import pytest
from pytest_reportportal import RPLogger, RPLogHandler



class Logger(object):
    def log(self):
        logging.setLoggerClass(RPLogger)
        logger = logging.getLogger(self)
        logger.setLevel(logging.DEBUG)
        # Create handler for Report Portal.
        rp_handler = RPLogHandler()
        # Set INFO level for Report Portal handler.
        rp_handler.setLevel(logging.DEBUG)
        # Add handler to the logger.
        logger.addHandler(rp_handler)
        return logger
