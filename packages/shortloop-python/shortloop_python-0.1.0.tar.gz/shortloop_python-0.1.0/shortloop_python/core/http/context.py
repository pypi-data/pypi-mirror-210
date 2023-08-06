from typing import Optional

import shortloop_python.core.model as model

from .http_request import HttpRequest
from .http_response import HttpResponse


class RequestResponseContext:
    def __init__(
        self,
        request=None,
        response=None,
        application_name=None,
        observed_api=None,
        api_config=None,
        agent_config=None,
        api_buffer_key=None,
        payload_capture_attempted=None,
        request_payload_capture_attempted=None,
        response_payload_capture_attempted=None,
        latency=None,
    ):
        self.request: Optional[HttpRequest] = request
        self.response: Optional[HttpResponse] = response
        self.application_name: Optional[str] = application_name
        self.observed_api: Optional[model.ObservedApi] = observed_api
        self.api_config: Optional[model.ApiConfig] = api_config
        self.agent_config: Optional[model.AgentConfig] = agent_config
        self.api_buffer_key: Optional[any] = api_buffer_key
        self.payload_capture_attempted: Optional[bool] = payload_capture_attempted
        self.request_payload_capture_attempted: Optional[bool] = request_payload_capture_attempted
        self.response_payload_capture_attempted: Optional[bool] = response_payload_capture_attempted
        self.latency: Optional[int] = latency

    def __str__(self):
        return (
            f"RequestResponseContext(request={self.request}, response={self.response}, "
            f"application_name={self.application_name}, observed_api={self.observed_api}, "
            f"api_config={self.api_config}, agent_config={self.agent_config}, "
            f"api_buffer_key={self.api_buffer_key}, "
            f"payload_capture_attempted={self.payload_capture_attempted}, "
            f"request_payload_capture_attempted={self.request_payload_capture_attempted}, "
            f"response_payload_capture_attempted={self.response_payload_capture_attempted}, "
            f"latency={self.latency})"
        )

    def __eq__(self, other):
        if not isinstance(other, RequestResponseContext):
            return False
        return (
            self.request == other.request
            and self.response == other.response
            and self.application_name == other.application_name
            and self.observed_api == other.observed_api
            and self.api_config == other.api_config
            and self.agent_config == other.agent_config
            and self.api_buffer_key == other.api_buffer_key
            and self.payload_capture_attempted == other.payload_capture_attempted
            and self.request_payload_capture_attempted == other.request_payload_capture_attempted
            and self.response_payload_capture_attempted == other.response_payload_capture_attempted
            and self.latency == other.latency
        )
