from threading import Semaphore

from shortloop_python.sdk_logger import logger

from ..http.http_connection import ShortLoopHttpConnection
from ..model import AgentConfig
from .abstract_buffer_manager import AbstractBufferManager
from .api_buffer_key import ApiBufferKey
from .buffer_manager_worker import BufferManagerWorker
from .simple_buffer import SimpleBuffer


class RegisteredApiBufferManager(AbstractBufferManager):
    def __init__(self, config_manager, shortloop_http_connection):
        super().__init__(config_manager)
        self.__shortloop_http_connection = shortloop_http_connection

    def create_worker(self, agent_config: AgentConfig) -> BufferManagerWorker:
        return RegisteredApiBufferManager.RegisteredApiBufferManagerWorker(
            agent_config, self.__shortloop_http_connection
        )

    class RegisteredApiBufferManagerWorker(BufferManagerWorker):
        def __init__(self, agent_config: AgentConfig, http_connection):
            super().__init__(agent_config)
            self.__semaphore = Semaphore(self.get_registered_api_count_to_capture())
            self.__http_connection: ShortLoopHttpConnection = http_connection

        def get_registered_api_count_to_capture(self):
            agent_config = super().get_operating_config()
            if not agent_config.registered_api_configs or len(agent_config.registered_api_configs) == 0:
                return 0

            total_apis = 0
            for api_config in agent_config.registered_api_configs:
                if api_config.buffer_size:
                    total_apis += api_config.buffer_size

            return total_apis

        def get_registered_api_buffer_size(self, api_buffer_key: ApiBufferKey):
            agent_config = super().get_operating_config()
            if not agent_config.registered_api_configs or len(agent_config.registered_api_configs) == 0:
                return 0

            for api_config in agent_config.registered_api_configs:
                if api_config.method == api_buffer_key.method and api_config.uri == api_buffer_key.uri:
                    return api_config.buffer_size

            return 0

        def init(self) -> bool:
            return True

        def offer(self, key: ApiBufferKey, sample) -> bool:
            if not self._buffer_map.get(key):
                self._buffer_map[key] = SimpleBuffer(self.get_registered_api_buffer_size(key))
            buffer = self._buffer_map.get(key)
            if buffer:
                return buffer.offer(sample)
            else:
                pass

            return False

        def can_offer(self, key: ApiBufferKey) -> bool:
            buffer_size = self.get_registered_api_buffer_size(key)
            if buffer_size == 0:
                return False

            buffer = self._buffer_map.get(key)

            if self.__semaphore.acquire(blocking=False):
                if buffer:
                    can_offer = True
                else:
                    can_offer = buffer.can_offer()
                self.__semaphore.release()
                return can_offer
            return False

        def sync_for_key(self, key: ApiBufferKey):
            try:
                buffer = self._buffer_map.get(key)
                if not buffer:
                    logger.error("Buffer is null for " + str(key.uri))
                    return
                iterations = buffer.size()
                if iterations == 0:
                    self._buffer_map.pop(key)
                    return
                while iterations > 0:
                    iterations -= 1
                    contents = []
                    sample = buffer.poll()
                    if not sample:
                        self._buffer_map.pop(key)
                        break
                    contents.append(sample)
                    self.__http_connection.send_samples(contents)
            except Exception as e:
                logger.error("Error inside syncForKey for key " + str(key.uri), exc_info=e)
