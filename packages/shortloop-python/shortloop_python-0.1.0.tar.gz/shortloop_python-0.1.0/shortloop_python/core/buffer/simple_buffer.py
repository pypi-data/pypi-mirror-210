import queue
from typing import Optional

from ..model import ApiSample
from .buffer import Buffer


class SimpleBuffer(Buffer):
    def __init__(self, max_size):
        self.__sample_queue = queue.Queue(max_size)

    def offer(self, sample: ApiSample) -> bool:
        try:
            self.__sample_queue.put(sample, block=False)
        except queue.Full:
            pass
        return True

    def can_offer(self):
        return not self.__sample_queue.full()

    def poll(self) -> Optional[ApiSample]:
        try:
            return self.__sample_queue.get(block=False)
        except queue.Empty:
            return None

    def clear(self):
        self.__sample_queue.queue.clear()

    def size(self):
        return self.__sample_queue.qsize()

    def __str__(self):
        return f"{str(self.__sample_queue)}"
