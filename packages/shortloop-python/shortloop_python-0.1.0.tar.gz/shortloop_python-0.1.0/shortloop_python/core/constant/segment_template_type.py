from enum import Enum


class SegmentTemplateType(str, Enum):
    NUMBER = "{number}"
    STRING = "{string}"
    UUID = "{uuid}"
    UNKNOWN = "{unknown}"
