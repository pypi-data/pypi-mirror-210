from datetime import datetime, timezone
from typing import List

from shortloop_python.core.model.api_config import ApiConfig
from shortloop_python.core.model.black_list_rule import BlackListRule


class AgentConfig:
    def __init__(
        self,
        buffer_sync_freq_in_sec: int,
        capture_api_sample: bool,
        config_fetch_freq_in_sec: int,
        registered_api_configs: List[ApiConfig],
        timestamp: str,
        discovery_buffer_size: int,
        discovery_buffer_size_per_api: int,
        black_list_rules: List[dict],
    ):
        self.buffer_sync_freq_in_sec: int = buffer_sync_freq_in_sec
        self.capture_api_sample: bool = capture_api_sample
        self.config_fetch_freq_in_sec: int = config_fetch_freq_in_sec
        self.registered_api_configs: List[ApiConfig] = list(
            map(lambda api_config: ApiConfig(api_config), registered_api_configs)
        )
        self.timestamp: datetime = datetime.fromisoformat(timestamp)
        self.discovery_buffer_size: int = discovery_buffer_size
        self.discovery_buffer_size_per_api: int = discovery_buffer_size_per_api
        self.black_list_rules: List[BlackListRule] = list(map(lambda rule: BlackListRule(rule), black_list_rules))

    def __str__(self) -> str:
        return (
            f"AgentConfig(buffer_sync_freq_in_sec={self.buffer_sync_freq_in_sec}, "
            f"capture_api_sample={self.capture_api_sample}, "
            f"config_fetch_freq_in_sec={self.config_fetch_freq_in_sec}, "
            f"registered_api_configs={str(self.registered_api_configs)}, "
            f"timestamp={self.timestamp}, "
            f"discovery_buffer_size={self.discovery_buffer_size}, "
            f"discovery_buffer_size_per_api={self.discovery_buffer_size_per_api}, "
            f"black_list_rules={str(self.black_list_rules)})"
        )

    @staticmethod
    def get_no_op_agent_config():
        epoch = datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        return AgentConfig(120, False, 120, [], epoch.isoformat(), 0, 0, [])
