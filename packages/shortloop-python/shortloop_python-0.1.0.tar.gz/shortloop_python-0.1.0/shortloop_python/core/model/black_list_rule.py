from typing import List

from ..constant import HttpMethod
from .uri import URI


class BlackListRule:
    def __init__(self, data: dict):
        self.black_list_type: str = data["blackListType"]
        self.match_values: List[str] = data["matchValues"]
        self.method: HttpMethod = data["method"]

    def is_valid(self) -> bool:
        if not self.black_list_type or not self.match_values:
            return False
        return True

    def matches_uri(self, uri: URI, method: HttpMethod) -> bool:
        if not self.is_valid():
            return False
        if not uri or not method:
            return False
        if self.method and self.method != method:
            return False
        if self.black_list_type.lower() == "endswith":
            for match_value in self.match_values:
                if uri.uri_path.lower().endswith(match_value.lower()):
                    return True
        elif self.black_list_type.lower() == "absolute":
            for match_value in self.match_values:
                if uri == URI.get_uri(match_value):
                    return True
        return False
