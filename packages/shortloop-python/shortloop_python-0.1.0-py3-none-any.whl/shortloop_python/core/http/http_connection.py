import json
from typing import List, Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from shortloop_python.sdk_logger import logger
from shortloop_python.sdk_version import SHORTLOOP_SDK_VERSION

from ..model import AgentConfig, ApiSample


class ShortLoopHttpConnection:
    def __init__(self, ct_url, auth_key, environment, capture):
        self.__base_url = ct_url
        self.__auth_key = auth_key
        self.__environment = environment
        self.__always_capture = capture == "always"
        self.__headers = {"Accept": "application/json", "Connection": "close", **SHORTLOOP_SDK_VERSION}

        if auth_key:
            self.__headers["authKey"] = self.__auth_key

        if environment and len(environment) > 0:
            self.__headers["environment"] = self.__environment

        if self.__always_capture:
            self.__headers["shortloop-capture"] = "always"

    def agent_config(self, agent_id, app_name) -> Optional[AgentConfig]:
        try:
            if len(self.__base_url) == 0:
                logger.error("ShortLoop base url is empty")
                return None

            query_params = {
                "agentId": agent_id,
                "appName": app_name,
            }

            url = self.__base_url + "/api/v1/agent-config"

            if query_params:
                url = url + "?" + urlencode(query_params)

            http_request = Request(url, method="GET", headers=self.__headers)

            with urlopen(http_request) as response:
                response_obj = json.load(response)
                return AgentConfig(
                    buffer_sync_freq_in_sec=response_obj["bufferSyncFreqInSec"],
                    capture_api_sample=response_obj["captureApiSample"],
                    config_fetch_freq_in_sec=response_obj["configFetchFreqInSec"],
                    registered_api_configs=response_obj["registeredApiConfigs"],
                    timestamp=response_obj["timestamp"],
                    discovery_buffer_size=response_obj["discoveryBufferSize"],
                    discovery_buffer_size_per_api=response_obj["discoveryBufferSizePerApi"],
                    black_list_rules=response_obj["blackListRules"],
                )
        except Exception as e:
            logger.error("Error while fetching agent config", exc_info=e)
            return None

    def send_samples(self, contents: List[ApiSample]):
        logger.debug(f"sending samples: [{','.join(map(lambda s: str(s), contents))}]")
        try:
            if len(self.__base_url) == 0:
                logger.error("ShortLoop base url is empty")
                return None

            json_samples = []
            for content in contents:
                json_samples.append(to_json(content))
            data = json.dumps(json_samples, ensure_ascii=False)

            url = self.__base_url + "/api/v1/data-ingestion/api-sample"

            if self.__always_capture:
                url = self.__base_url + "/api/v2/data-ingestion/api-sample"
            http_request = Request(url, method="POST", headers=self.__headers, data=data.encode("utf-8"))
            http_request.add_header("Content-Type", "application/json")
            with urlopen(http_request) as response:
                if not response.status == 200:
                    logger.error(f"Send Sample Request failed, API returned {response.status}")
                    return False

            return True
        except Exception as e:
            logger.error("Error while sending samples", exc_info=e)
            return False


def to_json(sample: ApiSample):
    data = {
        "rawUri": sample.raw_uri,
        "applicationName": sample.application_name,
        "hostName": sample.host_name,
        "port": int(sample.port) if sample.port and isinstance(sample.port, str) else sample.port,
        "scheme": sample.scheme,
        "method": sample.method,
        "statusCode": int(sample.status_code)
        if sample.status_code and isinstance(sample.status_code, str)
        else sample.status_code,
        "requestPayload": sample.request_payload,
        "responsePayload": sample.response_payload,
        "uncaughtExceptionMessage": sample.uncaught_exception_message,
        "payloadCaptureAttempted": sample.payload_capture_attempted,
        "requestPayloadCaptureAttempted": sample.request_payload_capture_attempted,
        "responsePayloadCaptureAttempted": sample.response_payload_capture_attempted,
        "latency": sample.latency,
    }

    params = {}
    req_headers = {}
    res_headers = {}

    if sample.parameters:
        keys = list(sample.parameters.keys())
        for key in keys:
            params[key] = sample.parameters.get(key)
    if sample.request_headers:
        keys = list(sample.request_headers.keys())
        for key in keys:
            req_headers[key] = sample.request_headers.get(key)
    if sample.response_headers:
        keys = list(sample.response_headers.keys())
        for key in keys:
            res_headers[key] = sample.response_headers.get(key)

    data["parameters"] = params
    data["requestHeaders"] = req_headers
    data["responseHeaders"] = res_headers

    return data
