from enum import Enum

from loguru import logger

from config import *
from config.config import RUNNING_ENV


class LogModules(Enum):
    PREDICT = 'predict'
    SERVICE = 'service'


def init_logger():
    # Server output to log file
    if CONFIG.ENV_RUN == RUNNING_ENV.LOCAL:
        path = CONFIG.LOG_DIR
        sink_info = f"{path}/batch_monitor-info.log"
        sink_error = f"{path}/batch_monitor-error.log"
        logger.add(
            sink=sink_info,
            format="{time} {level} {message}",
            level="INFO",
            rotation="10 MB",
            retention="30 days",
            compression="zip"
        )
        logger.add(
            sink=sink_error,
            format="{time} {level} {message}",
            level="ERROR",
            rotation="10 MB",
            retention="30 days",
            compression="zip"
        )
        init_module_logger()


def add_module_logger(module):
    logger_filename = CONFIG.LOG_DIR + "/batch_monitor-{}.log"
    filepath = logger_filename.format(module)
    logger.add(
        sink=filepath,
        format="{time} {level} {message}",
        level="INFO",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        filter=lambda x: x['name'].startswith(module)
    )
    return filepath


def init_module_logger():
    for name, member in LogModules.__members__.items():
        logger.info("Load log Module:{}, filepath:{}", name, add_module_logger(member.value))
