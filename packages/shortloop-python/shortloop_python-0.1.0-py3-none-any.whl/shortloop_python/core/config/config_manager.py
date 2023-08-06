from abc import ABC, abstractmethod

from .config_update_listener import ConfigUpdateListener


class ConfigManager(ABC):
    @abstractmethod
    def init(self) -> bool:
        pass

    @abstractmethod
    def subscribe_to_updates(self, config_update_listener: ConfigUpdateListener) -> bool:
        pass

    @abstractmethod
    def shutdown(self) -> bool:
        pass
