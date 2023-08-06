import random
from abc import ABC, abstractmethod
from typing import Dict, Optional

from shortloop_python.sdk_logger import logger

from ..model import AgentConfig
from ..scheduled_timer import ScheduledTimer
from .api_buffer_key import ApiBufferKey
from .buffer import Buffer


class BufferManagerWorker(ABC):
    def __init__(self, agent_config):
        self._buffer_map: Dict[ApiBufferKey, Buffer] = {}
        self.__agent_config: AgentConfig = agent_config
        self.__buffer_sync_timer: Optional[ScheduledTimer] = ScheduledTimer(
            self.__agent_config.buffer_sync_freq_in_sec, self.sync_for_keys
        )
        self.__buffer_sync_timer.setName("sl-buffer-" + str(random.randrange(0, 1000)))
        self.__buffer_sync_timer.start()

    @abstractmethod
    def init(self) -> bool:
        pass

    @abstractmethod
    def offer(self, key: ApiBufferKey, sample) -> bool:
        pass

    @abstractmethod
    def can_offer(self, key: ApiBufferKey) -> bool:
        pass

    @abstractmethod
    def sync_for_key(self, key: ApiBufferKey):
        pass

    def get_operating_config(self):
        return self.__agent_config

    def shutdown(self):
        try:
            logger.debug("Shutting down BufferManagerWorker")
            self.__buffer_sync_timer.cancel()
            self.clean_up_buffer_map()
        except Exception as e:
            logger.error("Error while shutting down BufferManagerWorker.__buffer_sync_timer", exc_info=e)

    def clean_up_buffer_map(self):
        self.sync_for_keys()
        for key in list(self._buffer_map.keys()):
            buffer = self._buffer_map.get(key)
            if buffer:
                buffer.clear()
        self._buffer_map.clear()

    def sync_for_keys(self):
        keys = list(self._buffer_map.keys())
        if keys and len(keys) == 0:
            return
        for key in keys:
            self.sync_for_key(key)
