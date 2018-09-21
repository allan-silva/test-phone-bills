import logging
import os


FMT = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s")


def configure_log(obj_instance, logger_name):
    logger = logging.getLogger(logger_name)
    if len(logger.handlers) == 0:
        logger.setLevel(int(os.getenv('LOG_LEVEL', logging.DEBUG)))
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(FMT)
        logger.addHandler(console_handler)
    obj_instance.log = logger
