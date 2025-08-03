import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from datetime import timedelta


class Loggers():
    def loggers():
        logger=logging.getLogger()
        logger.setLevel(logging.DEBUG)
        log_filename = datetime.now().strftime("logs/%d-%m-%Y.log")
        handler=TimedRotatingFileHandler(filename = log_filename,when = "midnight", interval = 1 , backupCount = 7)
        handler.setLevel(logging.DEBUG)
        formatter=logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # console_handler = logging.StreamHandler()
        # console_handler.setLevel(logging.INFO)
        # console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        # console_handler.setFormatter(console_formatter)
        # logger.addHandler(console_handler)
