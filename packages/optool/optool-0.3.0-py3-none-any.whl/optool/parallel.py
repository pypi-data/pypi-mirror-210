import os
from multiprocessing import Pool, current_process
from typing import Callable, Iterable

from pydantic import DirectoryPath, StrictInt

from optool import BaseModel
from optool.logging import LOGGER, LogFilter, LogLevels, setup_logger, timeit


def _get_system_cpu_counts() -> int:
    if count := os.cpu_count():
        return count
    raise ValueError("Cannot determine number of CPUs of this system.")


class ParallelExecutor(BaseModel):
    function: Callable
    log_sink: DirectoryPath
    log_level: LogLevels = 'TRACE'
    processes: StrictInt = _get_system_cpu_counts()

    @timeit(log_level='INFO')
    def run(self, *args):
        if len(args) == 1 and isinstance(args, Iterable):
            args = args[0]
        processes = min([self.processes, len(args)])
        LOGGER.info("Executing function {} on {} processes in parallel.", self.function.__name__, processes)
        # TODO: Figure out if this is actually necessary, and if so, how to extract the logger and add it again
        # LOGGER.remove()  # Default "sys.stderr" sink cannot be pickled
        with Pool(processes=processes) as pool:
            out = pool.map(self.run_subprocess, args)
        return out

    def run_subprocess(self, arg):
        self.setup_subprocess_logger()
        out = timeit(self.function, log_level='INFO')(arg)
        self.tear_down_subprocess_logger()
        return out

    def setup_subprocess_logger(self):
        process = current_process()
        log_file_name = str(self.log_sink.absolute() / f"log_{process.name}.log")
        setup_logger(sink=log_file_name, filter=LogFilter(), level=self.log_level)

    @staticmethod
    def tear_down_subprocess_logger():
        LOGGER.complete()  # make sure the queue (consumed by a thread started internally) is left in a stable state
