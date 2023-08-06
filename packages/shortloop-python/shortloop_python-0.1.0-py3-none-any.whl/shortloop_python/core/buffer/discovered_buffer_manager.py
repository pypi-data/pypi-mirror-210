from threading import Semaphore

from shortloop_python.sdk_logger import logger

from ..http.http_connection import ShortLoopHttpConnection
from ..model import AgentConfig
from .abstract_buffer_manager import AbstractBufferManager
from .api_buffer_key import ApiBufferKey
from .buffer_manager_worker import BufferManagerWorker
from .simple_buffer import SimpleBuffer


class DiscoveredApiBufferManager(AbstractBufferManager):
    def __init__(self, config_manager, shortloop_http_connection):
        super().__init__(config_manager)
        self.__shortloop_http_connection = shortloop_http_connection

    def create_worker(self, agent_config: AgentConfig) -> BufferManagerWorker:
        return DiscoveredApiBufferManager.DiscoveredApiBufferManagerWorker(
            agent_config, self.__shortloop_http_connection
        )

    class DiscoveredApiBufferManagerWorker(BufferManagerWorker):
        def __init__(self, agent_config: AgentConfig, http_connection):
            super().__init__(agent_config)
            self.__semaphore = Semaphore(agent_config.discovery_buffer_size)
            self.__http_connection: ShortLoopHttpConnection = http_connection

        def init(self) -> bool:
            return True

        def offer(self, key: ApiBufferKey, sample) -> bool:
            if not self._buffer_map.get(key):
                self._buffer_map[key] = SimpleBuffer(super().get_operating_config().discovery_buffer_size_per_api)
            buffer = self._buffer_map.get(key)
            if buffer:
                return buffer.offer(sample)
            else:
                pass
            return False

        def can_offer(self, key: ApiBufferKey) -> bool:
            if self.__semaphore.acquire(blocking=False):
                can_offer = False
                if super().get_operating_config().capture_api_sample:
                    buffer = self._buffer_map.get(key)
                    if buffer:
                        can_offer = buffer.can_offer()
                    else:
                        can_offer = len(self._buffer_map) < super().get_operating_config().discovery_buffer_size
                self.__semaphore.release()
                return can_offer
            return False

        def sync_for_key(self, key: ApiBufferKey):
            try:
                buffer = self._buffer_map.get(key)
                if not buffer:
                    return
                iterations = buffer.size()
                if iterations == 0:
                    self._buffer_map.pop(key)
                    return
                contents = []
                while iterations > 0:
                    iterations -= 1
                    sample = buffer.poll()
                    if not sample:
                        self._buffer_map.pop(key)
                        break
                    contents.append(sample)
                if len(contents) == 0:
                    return
                self.__http_connection.send_samples(contents)
            except Exception as e:
                logger.error("Error inside syncForKey for key " + str(key.uri), exc_info=e)
