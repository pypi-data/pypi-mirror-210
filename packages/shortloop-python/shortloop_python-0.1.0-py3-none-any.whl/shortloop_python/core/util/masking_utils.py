from typing import Dict, List


def get_masked_headers(headers: Dict[str, str], mask_headers: List[str]):
    if not headers or not mask_headers or len(mask_headers) == 0:
        return headers

    header_names = headers.keys()

    for header_name in header_names:
        if header_name.casefold() in (name.casefold() for name in mask_headers):
            headers[header_name] = "🔒MASKED🔒"
    return headers
