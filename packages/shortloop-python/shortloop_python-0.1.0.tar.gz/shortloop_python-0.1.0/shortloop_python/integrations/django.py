import re

from shortloop_python.core.http import HttpRequest, HttpResponse, RequestResponseContext
from shortloop_python.core.shortlook_sdk import auto_configuration


class ShortLoopDjangoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # TODO handle async

        # sometimes host contains port too
        host, port = self.get_host_port(request.get_host(), request.get_port())

        http_request = HttpRequest(
            raw_uri=request.path,
            hostname=host,
            scheme=request.scheme,
            port=port,
            method=request.method,
            headers=dict(request.headers.items()),
            params=dict(request.GET.lists()),
            body_raw=request.body,
        )

        ctx = RequestResponseContext(request=http_request)
        if auto_configuration and auto_configuration.filter:
            return auto_configuration.filter.process(ctx, self.wrap_get_response, request)
        else:
            return self.get_response(request)

    def wrap_get_response(self, *args, **kwargs):
        # response is the raw response of the next function. this is framework dependent.
        # return type can be None because maybe the next function doesn't return anything
        # regardless of the return type, we return this from the middleware so that it can be used in the chain
        #
        # http_response is parsed object of type shortloop_python.core.http.HttpResponse created from framework_response
        # this will never be None but it's properties can be.
        args = args if args is not None else []
        kwargs = kwargs if kwargs is not None else {}
        response = self.get_response(*args, **kwargs)
        return response, HttpResponse(
            headers=dict(response.headers.items()),
            status_code=response.status_code,
            body_raw=response.content,
        )

    @staticmethod
    def get_host_port(host: str, port: int):
        pattern = r"(.+?):(\d+)"
        match = re.match(pattern, host)
        if match:
            p_host = match.group(1)
            p_port = match.group(2)
            return p_host, p_port
        else:
            return host, port
