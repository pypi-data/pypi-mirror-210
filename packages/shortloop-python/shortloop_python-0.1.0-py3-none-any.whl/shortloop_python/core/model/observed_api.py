from typing import Optional

import shortloop_python.core.model as model

from ..constant import HttpMethod


class ObservedApi:
    def __init__(self, uri: str, method: HttpMethod):
        self.uri: model.URI = model.URI.get_non_templated_uri(uri)
        self.method: HttpMethod = method

    def matches(self, api_config: Optional[model.ApiConfig]) -> bool:
        if api_config is None:
            return False
        if self.method.value != api_config.method:
            return False
        return self.uri == api_config.uri
