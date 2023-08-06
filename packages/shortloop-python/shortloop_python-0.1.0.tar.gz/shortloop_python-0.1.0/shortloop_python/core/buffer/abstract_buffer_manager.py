from abc import ABC, abstractmethod
from typing import Optional

from ..config.config_manager import ConfigManager
from ..config.config_update_listener import ConfigUpdateListener
from ..model import AgentConfig
from .buffer_manager_worker import BufferManagerWorker
from .no_op_buffer_manager import NoOpBufferManagerWorker


class AbstractBufferManager(ConfigUpdateListener, ABC):
    def __init__(self, config_manager):
        self.__config_manager: ConfigManager = config_manager
        self.__dummy_worker: BufferManagerWorker = NoOpBufferManagerWorker()
        self.__worker: Optional[BufferManagerWorker] = self.__dummy_worker

    @abstractmethod
    def create_worker(self, agent_config: AgentConfig) -> BufferManagerWorker:
        pass

    @property
    def worker(self):
        return self.__worker

    def on_successful_config_update(self, agent_config: AgentConfig):
        if self.is_refresh_needed(self.__worker.get_operating_config(), agent_config):
            old_worker = self.__worker
            self.__worker = self.create_worker(agent_config)
            old_worker.shutdown()

    def on_erroneous_config_update(self):
        old_worker = self.__worker
        self.__worker = self.__dummy_worker
        old_worker.shutdown()

    def init(self):
        self.__config_manager.subscribe_to_updates(self)

    def shutdown(self):
        if self.__worker:
            self.__worker.shutdown()
            self.__worker = None
        return True

    @staticmethod
    def is_refresh_needed(older_config: AgentConfig, new_config: AgentConfig) -> bool:
        if new_config.timestamp.timestamp() == 0 and older_config.timestamp.timestamp() == 0:
            return False
        return new_config.timestamp > older_config.timestamp
