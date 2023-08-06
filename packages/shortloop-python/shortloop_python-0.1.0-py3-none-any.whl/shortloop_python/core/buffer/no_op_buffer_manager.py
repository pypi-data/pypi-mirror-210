from ..model import AgentConfig
from .api_buffer_key import ApiBufferKey
from .buffer_manager_worker import BufferManagerWorker


class NoOpBufferManagerWorker(BufferManagerWorker):
    def __init__(self):
        super().__init__(AgentConfig.get_no_op_agent_config())

    def init(self) -> bool:
        return True

    def offer(self, key: ApiBufferKey, sample) -> bool:
        pass

    def can_offer(self, key: ApiBufferKey) -> bool:
        pass

    def shutdown(self):
        return True

    def sync_for_key(self, key):
        return
