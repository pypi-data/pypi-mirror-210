from ..constant import HttpMethod
from ..model import URI, ApiConfig, ObservedApi


class ApiBufferKey:
    def __init__(self, uri, method):
        self.uri: URI = uri
        self.method: HttpMethod = method

    @staticmethod
    def get_api_buffer_key_from_observed_api(observed_api: ObservedApi):
        return ApiBufferKey(observed_api.uri, observed_api.method)

    @staticmethod
    def get_api_buffer_key_from_api_config(api_config: ApiConfig):
        return ApiBufferKey(api_config.uri, api_config.method)

    def __hash__(self):
        return hash((self.uri, self.method))

    def __eq__(self, other):
        if not isinstance(other, ApiBufferKey):
            return False
        return self.uri == other.uri and self.method == other.method

    def __str__(self):
        return f"ApiBufferKey({self.uri}, {self.method})"
