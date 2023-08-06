class ApiSample:
    def __init__(
        self,
        raw_uri,
        application_name,
        host_name,
        port,
        scheme,
        method,
        parameters,
        request_headers,
        response_headers,
        status_code,
        request_payload,
        response_payload,
        uncaught_exception_message,
        payload_capture_attempted,
        request_payload_capture_attempted,
        response_payload_capture_attempted,
        latency,
    ):
        self.raw_uri = raw_uri
        self.application_name = application_name
        self.host_name = host_name
        self.port = port
        self.scheme = scheme
        self.method = method
        self.parameters = parameters
        self.request_headers = request_headers
        self.response_headers = response_headers
        self.status_code = status_code
        self.request_payload = request_payload
        self.response_payload = response_payload
        self.uncaught_exception_message = uncaught_exception_message
        self.payload_capture_attempted = payload_capture_attempted
        self.request_payload_capture_attempted = request_payload_capture_attempted
        self.response_payload_capture_attempted = response_payload_capture_attempted
        self.latency = latency

    def __str__(self):
        return (
            f"ApiSample(raw_uri={self.raw_uri}, application_name={self.application_name}, "
            f"host_name={self.host_name}, port={self.port}, scheme={self.scheme}, method={self.method}, "
            f"parameters={self.parameters}, request_headers={self.request_headers}, "
            f"response_headers={self.response_headers}, status_code={self.status_code}, "
            f"request_payload={self.request_payload}, response_payload={self.response_payload}, "
            f"uncaught_exception_message={self.uncaught_exception_message}, "
            f"payload_capture_attempted={self.payload_capture_attempted}, "
            f"request_payload_capture_attempted={self.request_payload_capture_attempted}, "
            f"response_payload_capture_attempted={self.response_payload_capture_attempted}, "
            f"latency={self.latency})"
        )


def __eq__(self, other):
    if not isinstance(other, ApiSample):
        return False
    return (
        self.raw_uri == other.raw_uri
        and self.application_name == other.application_name
        and self.host_name == other.host_name
        and self.port == other.port
        and self.scheme == other.scheme
        and self.method == other.method
        and self.parameters == other.parameters
        and self.request_headers == other.request_headers
        and self.response_headers == other.response_headers
        and self.status_code == other.status_code
        and self.request_payload == other.request_payload
        and self.response_payload == other.response_payload
        and self.uncaught_exception_message == other.uncaught_exception_message
        and self.payload_capture_attempted == other.payload_capture_attempted
        and self.request_payload_capture_attempted == other.request_payload_capture_attempted
        and self.response_payload_capture_attempted == other.response_payload_capture_attempted
        and self.latency == other.latency
    )
