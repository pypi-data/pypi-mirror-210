from typing import Dict, List


class HttpRequest:
    def __init__(self, raw_uri, hostname, scheme, port, method, headers, params, body_raw=None, body=None):
        self.raw_uri = raw_uri
        self.hostname = hostname
        self.scheme: str = scheme
        self.port = port
        self.method: str = method
        self.headers: Dict[str, str] = headers
        self.params: Dict[str, List[str]] = params
        self.body_raw: any = body_raw
        self.body: str = body

    def __str__(self):
        return (
            f"HttpRequest(raw_uri={self.raw_uri}, hostname={self.hostname}, "
            f"scheme={self.scheme}, method={self.method}, headers={self.headers}, "
            f"params={self.params}, body_raw={self.body_raw} body={self.body})"
        )

    def __eq__(self, other):
        if not isinstance(other, HttpRequest):
            return False
        return (
            self.raw_uri == other.raw_uri
            and self.hostname == other.hostname
            and self.scheme == other.scheme
            and self.method == other.method
            and self.headers == other.headers
            and self.params == other.params
            and self.body_raw == other.body_raw
            and self.body == other.body
        )
