from abc import ABC, abstractmethod

from ..model import ApiSample


class Buffer(ABC):
    @abstractmethod
    def offer(self, sample: ApiSample) -> bool:
        pass

    @abstractmethod
    def can_offer(self):
        pass

    @abstractmethod
    def poll(self) -> ApiSample:
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def size(self):
        pass
