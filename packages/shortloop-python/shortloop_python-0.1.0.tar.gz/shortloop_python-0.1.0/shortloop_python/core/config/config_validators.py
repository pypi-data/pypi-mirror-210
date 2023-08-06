from shortloop_python.core.model.agent_config import AgentConfig
from shortloop_python.core.model.api_config import ApiConfig
from shortloop_python.core.model.uri import URI


def is_agent_config_valid(agent_config: AgentConfig) -> bool:
    if agent_config is None:
        return False

    if agent_config.buffer_sync_freq_in_sec is None:
        return False

    if agent_config.config_fetch_freq_in_sec is None:
        return False

    if agent_config.capture_api_sample is None:
        return False

    if agent_config.discovery_buffer_size is None:
        return False

    if agent_config.discovery_buffer_size_per_api is None:
        return False

    if agent_config.registered_api_configs is not None:
        for api_config in agent_config.registered_api_configs:
            if not is_api_config_valid(api_config):
                return False

    if agent_config.black_list_rules is not None:
        for black_list_rule in agent_config.black_list_rules:
            if not is_black_list_rule_valid(black_list_rule):
                return False

    return True


def is_api_config_valid(api_config: ApiConfig) -> bool:
    if api_config is None:
        return False

    if not is_uri_valid(api_config.uri):
        return False

    if api_config.method is None:
        return False

    if api_config.buffer_size is None:
        return False

    if api_config.capture_sample_request is None:
        return False

    if api_config.capture_sample_response is None:
        return False

    return True


def is_uri_valid(uri: URI) -> bool:
    if uri is None:
        return False

    if uri.uri_path is None:
        return False

    if len(uri.uri_path) == 0:
        return False

    return True


def is_black_list_rule_valid(black_list_rule) -> bool:
    if black_list_rule is None:
        return False

    if not black_list_rule.is_valid():
        return False

    return True
