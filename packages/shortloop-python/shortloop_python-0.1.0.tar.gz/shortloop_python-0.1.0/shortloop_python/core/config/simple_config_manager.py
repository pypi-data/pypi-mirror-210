from enum import Enum
from threading import Timer
from typing import List, Optional

from shortloop_python.sdk_logger import logger

from ..http.http_connection import ShortLoopHttpConnection
from ..model.agent_config import AgentConfig
from ..model.sdk_options import SdkOptions
from .config_manager import ConfigManager
from .config_update_listener import ConfigUpdateListener
from .config_validators import is_agent_config_valid


class SimpleConfigManager(ConfigManager):
    class ConfigOrError:
        class ErrorCode(Enum):
            TIMEOUT = 1
            PARSE_ERROR = 2
            INVALID_CONFIG = 3

        def __init__(self, agent_config=None, error_code=None):
            self.agent_config: AgentConfig = agent_config
            self.error_code: SimpleConfigManager.ConfigOrError.ErrorCode = error_code

        def __str__(self) -> str:
            return f"ConfigOrError(agent_config={self.agent_config}, " f"error_code={self.error_code})"

    def __init__(self, opts: SdkOptions, http_connection, agent_id):
        self.__app_name = opts.application_name
        self.__http_connection: ShortLoopHttpConnection = http_connection
        self.__agent_id = agent_id
        self.__config_update_listeners: List[ConfigUpdateListener] = []
        self.__execution_service: Optional[Timer] = None

    def init(self) -> bool:
        try:
            self.schedule_config_refresh(60)
            return True
        except Exception as e:
            logger.error("Error in SimpleConfigManager.init", exc_info=e)
            return False

    def subscribe_to_updates(self, config_update_listener) -> bool:
        self.__config_update_listeners.append(config_update_listener)
        return True

    def shutdown(self) -> bool:
        logger.debug("Shutting down SimpleConfigManager")
        try:
            self.__execution_service.cancel()
            return True
        except Exception as e:
            logger.error("Error while shutting down SimpleConfigManager.__execution_service", exc_info=e)
            return False

    def schedule_config_refresh(self, time_sec: int):
        if self.__execution_service and self.__execution_service.is_alive():
            self.__execution_service.cancel()
        self.__execution_service = Timer(time_sec, self.fetch_config_notify)
        self.__execution_service.start()

    def fetch_config_notify(self) -> None:
        config_or_error: SimpleConfigManager.ConfigOrError = self.fetch_config()
        if config_or_error.error_code:
            self.schedule_config_refresh(60)
            self.on_unsuccessful_config_fetch()
        else:
            if config_or_error.agent_config:
                self.schedule_config_refresh(config_or_error.agent_config.config_fetch_freq_in_sec)
                self.on_successful_config_fetch(config_or_error.agent_config)

    def fetch_config(self) -> ConfigOrError:
        try:
            agent_config = self.__http_connection.agent_config(agent_id=self.__agent_id, app_name=self.__app_name)
            if agent_config is not None:
                if is_agent_config_valid(agent_config):
                    return SimpleConfigManager.ConfigOrError(agent_config)
                else:
                    logger.error("Received invalid config: %s", str(agent_config))
                    return SimpleConfigManager.ConfigOrError(
                        error_code=SimpleConfigManager.ConfigOrError.ErrorCode.INVALID_CONFIG
                    )
            else:
                return SimpleConfigManager.ConfigOrError(
                    error_code=SimpleConfigManager.ConfigOrError.ErrorCode.INVALID_CONFIG
                )
        except Exception as e:
            logger.error("Error while parsing config", exc_info=e)
            return SimpleConfigManager.ConfigOrError(error_code=SimpleConfigManager.ConfigOrError.ErrorCode.PARSE_ERROR)

    def on_successful_config_fetch(self, agent_config: AgentConfig) -> None:
        for listener in self.__config_update_listeners:
            listener.on_successful_config_update(agent_config)

    def on_unsuccessful_config_fetch(self) -> None:
        for listener in self.__config_update_listeners:
            listener.on_erroneous_config_update()
