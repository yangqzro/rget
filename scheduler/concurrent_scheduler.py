import os
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Iterator, Tuple, TypeVar, TypeVarTuple

Params = TypeVarTuple("Params")
Result = TypeVar("Result")


class ConScheduler:
    def __init__(self, max_task_concurrent: int = 8, max_workers: int = os.cpu_count() + 4):
        self.__semaphore = threading.Semaphore(max_task_concurrent)
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def call(self, task: Callable[[*Params], Result], *args: *Params) -> Result:
        with self.__semaphore:
            return task(*args)

    def submit(self, task: Callable[[*Params], Result], *args: *Params):
        return self._executor.submit(lambda args: self.call(task, *args), args)

    def map(self, task: Callable[[*Params], Result], args_iter: Iterator[Tuple[*Params]]) -> Iterator[Result]:
        return self._executor.map(lambda args: self.call(task, *args), args_iter)

    def shutdown(self):
        self._executor.shutdown()

    def __enter__(self):
        return self

    def __exit__(self, t, v, tb):
        self.shutdown()
