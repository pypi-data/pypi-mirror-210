from typing import List

from shortloop_python.core.util.uri_utils import (
    are_path_segments_matching,
    get_path_segments,
    is_path_segment_template,
)


class URI:
    def __init__(self, data: dict):
        self.uri_path: str = data["uriPath"]
        self.has_path_variable: bool = data["hasPathVariable"]

    @staticmethod
    def get_non_templated_uri(uri_path: str):
        return URI({"uriPath": uri_path, "hasPathVariable": False})

    @staticmethod
    def get_uri(uri_path: str):
        path_segments = get_path_segments(uri_path)
        is_templated_uri = False
        for path_segment in path_segments:
            if is_path_segment_template(path_segment):
                is_templated_uri = True
                break
        return URI({"uriPath": uri_path, "hasPathVariable": is_templated_uri})

    def __str__(self):
        return f"URI(uri_path='{self.uri_path}', has_path_variable={self.has_path_variable})"

    def __hash__(self):
        return hash((self.uri_path, self.has_path_variable))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, URI) or other is None:
            return False
        if not self.has_path_variable and not other.has_path_variable and self.uri_path == other.uri_path:
            return True
        path_segments = get_path_segments(self.uri_path)
        other_path_segments = get_path_segments(other.uri_path)
        if len(path_segments) != len(other_path_segments):
            return False
        for idx in range(len(path_segments)):
            path_segment = path_segments[idx]
            other_path_segment = other_path_segments[idx]
            if not are_path_segments_matching(path_segment, other_path_segment):
                return False
        return True

    def get_size(self) -> int:
        return len(get_path_segments(self.uri_path))

    def get_path_segments(self) -> List[str]:
        return get_path_segments(self.uri_path)
