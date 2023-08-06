import random
from typing import Optional

from shortloop_python.core.filter import AlwaysCaptureShortLoopFilter, ShortLoopFilter
from shortloop_python.sdk_logger import logger, set_logging_config

from .always_capture_sync import ShortloopDataSyncService
from .api_processor import ApiProcessor
from .buffer.discovered_buffer_manager import DiscoveredApiBufferManager
from .buffer.registered_buffer_manager import RegisteredApiBufferManager
from .config.simple_config_manager import SimpleConfigManager
from .http.http_connection import ShortLoopHttpConnection
from .model.sdk_options import SdkOptions


class ShortLoopAutoConfiguration:
    def __init__(self, opts):
        self.__opts: SdkOptions = opts
        self.__filter: Optional[ShortLoopFilter] = None

    def init(self):
        agent_id = str(random.randrange(100000))
        set_logging_config(self.__opts.logging_enabled, self.__opts.log_level)

        http_connection = ShortLoopHttpConnection(
            ct_url=self.__opts.url,
            auth_key=self.__opts.auth_key,
            environment=self.__opts.environment,
            capture=self.__opts.capture,
        )

        if self.__opts.capture == "always":
            data_sync_service = ShortloopDataSyncService(shortloop_http_connection=http_connection)
            data_sync_service.init()

            api_processor = ApiProcessor(
                mask_headers=self.__opts.mask_headers,
                discovered_api_buffer_manager=None,
                registered_api_buffer_manager=None,
                data_sync_service=data_sync_service,
            )

            self.__filter = AlwaysCaptureShortLoopFilter(
                api_processor=api_processor, application_name=self.__opts.application_name
            )

            logger.debug('ShortLoopAutoConfiguration.__opts.capture == "always"')

            return

        config_manager = SimpleConfigManager(opts=self.__opts, agent_id=agent_id, http_connection=http_connection)
        config_manager.init()

        discovered_buffer_manager = DiscoveredApiBufferManager(
            config_manager=config_manager, shortloop_http_connection=http_connection
        )
        logger.debug("discovered_buffer_manager.init")
        discovered_buffer_manager.init()

        registered_buffer_manager = RegisteredApiBufferManager(
            config_manager=config_manager, shortloop_http_connection=http_connection
        )
        logger.debug("registered_buffer_manager.init")
        registered_buffer_manager.init()

        api_processor = ApiProcessor(
            mask_headers=self.__opts.mask_headers,
            discovered_api_buffer_manager=discovered_buffer_manager,
            registered_api_buffer_manager=registered_buffer_manager,
        )

        self.__filter = ShortLoopFilter(
            config_manager=config_manager, api_processor=api_processor, application_name=self.__opts.application_name
        )
        logger.debug("ShortLoopAutoConfiguration.__filter.init")
        self.__filter.init()

    @property
    def filter(self) -> Optional[ShortLoopFilter]:
        return self.__filter
