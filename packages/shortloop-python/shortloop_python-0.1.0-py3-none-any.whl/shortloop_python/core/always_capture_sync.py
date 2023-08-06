import concurrent.futures
from threading import BoundedSemaphore

from shortloop_python.sdk_logger import logger

from .http.http_connection import ShortLoopHttpConnection


class ShortloopDataSyncService:
    def __init__(self, shortloop_http_connection):
        self.__shortloop_http_connection: ShortLoopHttpConnection = shortloop_http_connection
        self.__drop_count = 0
        self.__executor_service = None
        self.__semaphore = BoundedSemaphore(5)

    def init(self):
        try:
            self.__executor_service = concurrent.futures.ThreadPoolExecutor(
                max_workers=2, thread_name_prefix="sl-sync-"
            )
        except Exception as e:
            logger.error("Error in ShortloopDataSyncService.init", exc_info=e)
            return False
        return True

    def sync_data(self, api_sample):
        try:
            if api_sample is None:
                return

            def send_samples():
                samples = [api_sample]
                result = self.__shortloop_http_connection.send_samples(samples)
                if not result:
                    self.__drop_count += 1
                    logger.info(f"Dropped {self.__drop_count} samples")
                self.__semaphore.release()

            if self.__semaphore.acquire(blocking=False):
                self.__executor_service.submit(send_samples)
            else:
                self.__drop_count += 1
                logger.info(f"Dropped {self.__drop_count} samples")
        except Exception as e:
            logger.error("Error in ShortloopDataSyncService.sync_data", exc_info=e)
