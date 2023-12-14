import time
import warnings
from functools import wraps

from loguru import logger

warnings.simplefilter("ignore")
warnings.filterwarnings("ignore")

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def func_timer(function):
    """
    Implement function timing with decorators
    :param function: Functions that require timing
    :return: None
    """
    @wraps(function)
    def function_timer(*args, **kwargs):
        logger.info('[Function: {name} start...]'.format(name=function.__name__))
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        logger.info('[Function: {name} finished, spent time: {time:.3f}s]'.format(name=function.__name__,
                                                                                  time=t1 - t0))
        return result

    return function_timer
