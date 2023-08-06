from shortloop_python.core.api_processor import ApiProcessor
from shortloop_python.core.buffer.api_buffer_key import ApiBufferKey
from shortloop_python.core.http.context import RequestResponseContext
from shortloop_python.core.util.filter_utils import get_observed_api_from_request
from shortloop_python.sdk_logger import logger


class AlwaysCaptureShortLoopFilter:
    def __init__(self, api_processor, application_name):
        self.__api_processor: ApiProcessor = api_processor
        self.__application_name: str = application_name

    def process(self, ctx: RequestResponseContext, next_fn, *args, **kwargs):
        try:
            observed_api = get_observed_api_from_request(ctx.request)

            ctx.application_name = self.__application_name
            ctx.observed_api = observed_api
            ctx.api_buffer_key = ApiBufferKey.get_api_buffer_key_from_observed_api(observed_api)

            return self.__api_processor.process_always_capture(ctx, next_fn, *args, **kwargs)
        except Exception as e:
            logger.error("Error in ShortLoopFilter.process", exc_info=e)
            return next_fn(*args, **kwargs)[0]
