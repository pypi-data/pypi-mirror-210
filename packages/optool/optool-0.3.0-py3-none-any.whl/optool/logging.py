import time
from fnmatch import fnmatch
from functools import wraps
from io import TextIOWrapper
from types import FunctionType, MethodType
from typing import Any, Callable, Dict, List, Literal, Optional, Union

from loguru import logger
from pydantic import StrictStr, validate_arguments

from optool.fields.misc import NonEmptyStr

LogLevels = Literal['TRACE', 'DEBUG', 'INFO', 'SUCCESS', 'WARNING', 'ERROR', 'CRITICAL']


class MessageFilter:
    __slots__ = 'module', 'function', 'process', 'level'

    @validate_arguments
    def __init__(self,
                 module: Optional[NonEmptyStr] = None,
                 function: Optional[NonEmptyStr] = None,
                 process: Optional[NonEmptyStr] = None,
                 level: LogLevels = 'CRITICAL'):

        self.module = module
        self.function = function
        self.process = process
        self.level = logger.level(level)

    def is_accepted(self, record: Dict[str, Any]) -> bool:
        if self.module is not None and self.module != record["name"]:
            return True
        if self.function is not None and self.function != record["function"]:
            return True
        if self.process is not None and self.process != record["process"].process__name:
            return True

        return record["level"].no >= self.level.no


class LogFilter:
    __slots__ = 'level', 'process', '_filters'

    @validate_arguments
    def __init__(self, *, minimum_level: LogLevels = 'TRACE', process: StrictStr = "*"):
        self.level = logger.level(minimum_level)
        self.process = process
        self._filters: List[MessageFilter] = []

    def __call__(self, record):
        if (record["level"].no < self.level.no) or not fnmatch(record["process"].name, self.process):
            return False

        # noinspection PyShadowingBuiltins
        return all(filter.is_accepted(record) for filter in self._filters)

    # noinspection PyShadowingBuiltins
    def add(self, filter: Union[MessageFilter, List[MessageFilter]]):
        if isinstance(filter, MessageFilter):
            self._filters.append(filter)
        else:
            self._filters.extend(filter)


FORMAT = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {process.name} | <level>{level: <8}</level> | " \
         "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>{exception}"

logger_settings = dict(
    # rotation="10 MB",
    serialize=False,
    format=FORMAT,
    # format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
    diagnose=True,
    backtrace=True,
    enqueue=True,
)


# noinspection PyShadowingBuiltins
def setup_logger(sink, filter, level):
    logger.remove()
    if isinstance(sink, TextIOWrapper):
        logger.add(sink, filter=filter, level=level, **logger_settings)
    elif isinstance(sink, str):
        logger.add(sink, mode="w", filter=filter, level=level, **logger_settings)
    else:
        raise ValueError(f"The sink must either be a TextIOWrapper or a string, "
                         f"but is {sink.__class__.__name__!r}.")


LOGGER = logger


def time_function(func, log_level, *args, **kwargs):
    # See https://loguru.readthedocs.io/en/stable/resources/recipes.html#
    # logging-entry-and-exit-of-functions-with-a-decorator
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    LOGGER.log(log_level, "Function {!r} executed in {:f} s.", func.__name__, end - start)
    return result


def timeit(func: Optional[Union[Callable, FunctionType, MethodType]] = None, /, *, log_level: str = "DEBUG"):

    def func_wrapper(*args, **kwargs):
        return time_function(func, log_level, *args, **kwargs)

    if func is not None:
        return func_wrapper

    # Need to wrap it one more time as func is None
    # noinspection PyShadowingNames
    def timeit_decorator(func):

        @wraps(func)
        def function_wrapper(*args, **kwargs):
            return time_function(func, log_level, *args, **kwargs)

        return function_wrapper

    return timeit_decorator
