import logging
import os


FMT = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s")


def configure_log(obj_instance, logger_name):
    console_handler = logging.StreamHandler()
    logger = logging.getLogger(logger_name)
    logger.setLevel(os.getenv('LOG_LEVEL', logging.DEBUG))
    console_handler.setFormatter(FMT)
    logger.addHandler(console_handler)
    obj_instance.log = logger
