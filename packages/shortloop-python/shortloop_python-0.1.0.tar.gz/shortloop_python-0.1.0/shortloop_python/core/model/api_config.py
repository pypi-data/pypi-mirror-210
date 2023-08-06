from ..constant import HttpMethod
from .uri import URI


class ApiConfig:
    def __init__(self, data: dict):
        self.uri: URI = URI(data["uri"])
        self.method: HttpMethod = data["method"]
        self.buffer_size: int = data["bufferSize"]
        self.capture_sample_request: bool = data["captureSampleRequest"]
        self.capture_sample_response: bool = data["captureSampleResponse"]

    def __str__(self):
        return (
            f"ApiConfig(uri={str(self.uri)}, method={self.method}, buffer_size={self.buffer_size}, "
            f"capture_sample_request={self.capture_sample_request}, "
            f"capture_sample_response={self.capture_sample_response})"
        )
