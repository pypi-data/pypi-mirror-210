from typing import List, Optional

from ..constant import HttpMethod
from ..http.http_request import HttpRequest
from ..model import AgentConfig, ApiConfig, BlackListRule, ObservedApi


def get_api_config(observed_api: ObservedApi, agent_config: AgentConfig) -> Optional[ApiConfig]:
    if not len(agent_config.registered_api_configs) > 0:
        return None
    registered_api_configs = agent_config.registered_api_configs
    for api_config in registered_api_configs:
        if observed_api.matches(api_config):
            return api_config

    return None


def get_observed_api_from_request(request: HttpRequest):
    method = HttpMethod(request.method)
    return ObservedApi(request.raw_uri, method)


def is_blacklisted_api(observed_api: ObservedApi, agent_config: AgentConfig) -> bool:
    try:
        if not agent_config or not agent_config.black_list_rules:
            return False
        blacklist_rules: List[BlackListRule] = agent_config.black_list_rules
        for blacklist_rule in blacklist_rules:
            if blacklist_rule.matches_uri(observed_api.uri, observed_api.method):
                return True
    except Exception:
        pass
    return False
