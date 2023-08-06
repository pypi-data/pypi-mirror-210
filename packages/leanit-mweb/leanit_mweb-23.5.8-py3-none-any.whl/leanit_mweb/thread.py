from __future__ import annotations
import logging
import threading
import weakref
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures.thread import _worker, _threads_queues
from functools import wraps

logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    pass

class AdvancedThreadPoolExecutor(ThreadPoolExecutor):
    def __init__(self, min_workers=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._min_workers = min_workers
        if self._min_workers:
            self._warmup_threads(self._min_workers)

        # counter of busy threads
        self._busy_counter = 0

    def submit(self, fn, *args, **kwargs):
        fn = self._wrap_task(fn)
        return super().submit(fn, *args, **kwargs)

    def _wrap_task(self, fn: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # increment the busy counter
            self._busy_counter += 1
            try:
                # call the original function
                return fn(*args, **kwargs)
            finally:
                # decrement the busy counter
                self._busy_counter -= 1

        return wrapper

    def _warmup_threads(self, thread_count: int):
        if thread_count > self._max_workers:
            raise RuntimeError(f"Cannot warmup more threads ({thread_count}) than max_workers ({self._max_workers})")

        # When the executor gets lost, the weakref callback will wake up
        # the worker threads.
        def weakref_cb(_, q=self._work_queue):
            q.put(None)

        num_threads = len(self._threads)
        while num_threads < thread_count:
            thread_name = '%s_%d' % (self._thread_name_prefix or self,
                                     num_threads)
            t = threading.Thread(name=thread_name, target=_worker,
                                 args=(weakref.ref(self, weakref_cb),
                                       self._work_queue,
                                       self._initializer,
                                       self._initargs))
            t.start()
            self._threads.add(t)
            _threads_queues[t] = self._work_queue
            num_threads += 1
