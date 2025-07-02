import os
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Iterator, Tuple, TypeVar, TypeVarTuple

TaskParams = TypeVarTuple("TaskParams")
TaskResult = TypeVar("TaskResult")


class ConScheduler:
    def __init__(self, max_task_concurrent: int = 8, max_workers: int = os.cpu_count() + 4):
        self._semaphore = threading.Semaphore(max_task_concurrent)
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def call(self, task: Callable[[*TaskParams], TaskResult], *args: *TaskParams) -> TaskResult:
        with self._semaphore:
            return task(*args)

    def submit(self, task: Callable[[*TaskParams], TaskResult], *args: *TaskParams):
        return self._executor.submit(lambda args: self.call(task, *args), args)

    def map(
        self, task: Callable[[*TaskParams], TaskResult], args_iter: Iterator[Tuple[*TaskParams]]
    ) -> Iterator[TaskResult]:
        return self._executor.map(lambda args: self.call(task, *args), args_iter)

    def shutdown(self):
        self._executor.shutdown()

    def __enter__(self):
        return self

    def __exit__(self, t, v, tb):
        self.shutdown()
