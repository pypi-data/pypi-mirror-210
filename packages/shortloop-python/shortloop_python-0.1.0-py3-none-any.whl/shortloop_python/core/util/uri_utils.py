from typing import List


def get_path_segments(uri: str) -> List[str]:
    if not uri:
        return []
    return [segment for segment in uri.split("/") if len(segment) > 0]


def are_path_segments_matching(path_variable_a: str, path_variable_b: str) -> bool:
    if path_variable_a is None and path_variable_b is None:
        return True
    if path_variable_a and path_variable_b:
        if path_variable_a == path_variable_b:
            return True
        is_path_variable_a_template = is_path_segment_template(path_variable_a)
        is_path_variable_b_template = is_path_segment_template(path_variable_b)
        return is_path_variable_a_template or is_path_variable_b_template
    return False


def is_path_segment_template(path_segment: str) -> bool:
    if path_segment is None:
        return False
    path_segment = path_segment.strip()
    return path_segment.startswith("{") and path_segment.endswith("}")
