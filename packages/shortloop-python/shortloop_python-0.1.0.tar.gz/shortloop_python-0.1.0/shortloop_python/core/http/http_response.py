class HttpResponse:
    def __init__(
        self,
        headers,
        status_code,
        body_raw=None,
        body=None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body_raw = body_raw
        self.body = body
