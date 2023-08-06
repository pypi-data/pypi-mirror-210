import logging
import sys
from typing import Union

logger = logging.getLogger("shortloop_python")
logger.propagate = False

stream_handler = logging.StreamHandler(stream=sys.stdout)
stream_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(threadName)s %(message)s"))
logger.addHandler(stream_handler)


def set_logging_config(enabled: bool, level: Union[int, str]):
    global logger
    if not enabled:
        # effectively disables logging
        logger.setLevel(logging.CRITICAL + 1)
    else:
        logger.setLevel(level)
