import time

from shortloop_python.sdk_logger import logger

from .always_capture_sync import ShortloopDataSyncService
from .buffer.buffer_manager_worker import BufferManagerWorker
from .buffer.discovered_buffer_manager import DiscoveredApiBufferManager
from .buffer.registered_buffer_manager import RegisteredApiBufferManager
from .http import RequestResponseContext
from .model.api_sample import ApiSample
from .util.masking_utils import get_masked_headers


class ApiProcessor:
    def __init__(
        self,
        mask_headers,
        registered_api_buffer_manager=None,
        discovered_api_buffer_manager=None,
        data_sync_service=None,
    ):
        self.__mask_headers = mask_headers
        self.__data_sync_service: ShortloopDataSyncService = data_sync_service
        self.__registered_api_buffer_manager: RegisteredApiBufferManager = registered_api_buffer_manager
        self.__discovered_api_buffer_manager: DiscoveredApiBufferManager = discovered_api_buffer_manager

    def process_always_capture(self, ctx: RequestResponseContext, next_fn, *args, **kwargs):
        start_time = time.time()
        framework_response, http_response = next_fn(*args, **kwargs)
        end_time = time.time()
        ctx.response = http_response

        ctx.request.body = str(ctx.request.body_raw, "utf-8")
        ctx.response.body = str(ctx.response.body_raw, "utf-8")

        ctx.latency = (end_time - start_time) * 1000
        ctx.payload_capture_attempted = True
        ctx.request_payload_capture_attempted = True
        ctx.response_payload_capture_attempted = True

        self.__try_offering_always_capture(ctx)

        return framework_response

    def __try_offering_always_capture(self, ctx: RequestResponseContext):
        try:
            logger.debug("ApiProcessor.__try_offering_always_capture")
            api_sample = self.__get_sample_from_context(ctx)
            self.__data_sync_service.sync_data(api_sample)
        except Exception as e:
            logger.error("Error in ApiProcessor.__try_offering_always_capture", exc_info=e)

    def process_discovered_api(self, ctx: RequestResponseContext, next_fn, *args, **kwargs):
        worker = self.__discovered_api_buffer_manager.worker
        if not worker:
            logger.error("__discovered_api_buffer_manager.worker is None inside process_discovered_api")
            return next_fn(*args, **kwargs)[0]

        can_offer = worker.can_offer(ctx.api_buffer_key)
        ctx.payload_capture_attempted = False

        framework_response, http_response = next_fn(*args, **kwargs)
        ctx.response = http_response
        ctx.request.body = None
        ctx.response.body = None

        if can_offer and worker:
            self.__try_offering(ctx, worker)

        return framework_response

    def process_registered_api(self, ctx: RequestResponseContext, next_fn, *args, **kwargs):
        worker = self.__registered_api_buffer_manager.worker
        if not worker:
            logger.error("__registered_api_buffer_manager.worker is None inside process_registered_api")
            return next_fn(*args, **kwargs)[0]

        can_offer = True

        start_time = time.time()
        framework_response, http_response = next_fn(*args, **kwargs)
        end_time = time.time()

        ctx.response = http_response

        request_payload_capture_attempted = self.__should_capture_request(ctx)
        if not request_payload_capture_attempted:
            ctx.request.body = None
        elif ctx.request.body_raw:
            ctx.request.body = str(ctx.request.body_raw, "utf-8")

        response_payload_capture_attempted = self.__should_capture_response(ctx)
        if not response_payload_capture_attempted:
            ctx.response.body = None
        elif ctx.response.body_raw:
            ctx.response.body = str(ctx.response.body_raw, "utf-8")

        ctx.latency = (end_time - start_time) * 1000
        ctx.payload_capture_attempted = True
        ctx.request_payload_capture_attempted = request_payload_capture_attempted
        ctx.response_payload_capture_attempted = response_payload_capture_attempted

        if can_offer and worker:
            self.__try_offering(ctx, worker)

        return framework_response

    def __try_offering(self, ctx: RequestResponseContext, worker: BufferManagerWorker):
        try:
            logger.debug("ApiProcessor.__try_offering")
            api_sample = self.__get_sample_from_context(ctx)
            worker.offer(ctx.api_buffer_key, api_sample)
        except Exception as e:
            logger.error("Error in ApiProcessor.__try_offering", exc_info=e)

    @staticmethod
    def __should_capture_request(ctx: RequestResponseContext) -> bool:
        return ctx and ctx.api_config and ctx.api_config.capture_sample_request

    @staticmethod
    def __should_capture_response(ctx: RequestResponseContext) -> bool:
        return ctx and ctx.api_config and ctx.api_config.capture_sample_response

    def __get_sample_from_context(self, ctx: RequestResponseContext):
        api_sample = ApiSample(
            raw_uri=ctx.request and ctx.request.raw_uri,
            method=ctx.request and ctx.request.method,
            application_name=ctx.application_name,
            host_name=ctx.request.hostname,
            port=ctx.request.port,
            scheme=ctx.request and ctx.request.scheme,
            parameters=ctx.request and ctx.request.params,
            request_headers=ctx.request and get_masked_headers(ctx.request.headers, self.__mask_headers),
            response_headers=ctx.response and get_masked_headers(ctx.response.headers, self.__mask_headers),
            status_code=ctx.response and ctx.response.status_code,
            request_payload=ctx.request and ctx.request.body,
            response_payload=ctx.response and ctx.response.body,
            uncaught_exception_message=None,
            payload_capture_attempted=ctx.payload_capture_attempted,
            request_payload_capture_attempted=ctx.request_payload_capture_attempted,
            response_payload_capture_attempted=ctx.response_payload_capture_attempted,
            latency=ctx.latency,
        )

        if ctx.api_config:
            api_sample.method = ctx.api_config.method
        else:
            api_sample.method = ctx.observed_api.method

        return api_sample
