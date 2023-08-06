from abc import ABC, abstractmethod

from shortloop_python.core.model.agent_config import AgentConfig


class ConfigUpdateListener(ABC):
    @abstractmethod
    def on_successful_config_update(self, agent_config: AgentConfig):
        pass

    @abstractmethod
    def on_erroneous_config_update(self):
        pass
