import logging
from typing import List, Optional, Union

from shortloop_python.core.model.sdk_options import SdkOptions

from .auto_configuration import ShortLoopAutoConfiguration

options: Optional[SdkOptions] = None
initialized = False
auto_configuration: Optional[ShortLoopAutoConfiguration] = None


def init(
    url: str = "",
    application_name: str = "",
    environment: str = "",
    auth_key: str = None,
    logging_enabled: bool = False,
    log_level: Union[str, int] = logging.FATAL,
    mask_headers: Optional[List[str]] = None,
    capture: str = None,
):
    """
    Initialize ShortLoop SDK. It automatically samples traffic and syncs with ShortLoop servers.


    :param str url: The ShortLoop url for your org, provided by ShortLoop team.
        Ex: https://example.shortloop.dev or https://shortloop.example.com

    :param str application_name: Project or Application name. Ex: Demo-Service

    :param str auth_key: ShortLoop auth key, provided by ShortLoop team.

    :param str environment: Your application environment. Ex: stage, prod, alpha, etc.

    :param bool logging_enabled: Enable ShortLoop SDK logging

    :param str log_level: ShortLoop SDK logging level. Logging depends on `logging_enabled ` argument.

    :param list(int) mask_headers: Headers names (case in-sensitive) that will be masked at the SDK level itself.
        Masking will happen locally before data is sent to ShortLoop servers. Ex: ["cookie", "x-auth"]

    :param str capture: TEST MODE
    """
    global options, initialized, auto_configuration

    if not initialized:
        initialized = True

        opts: SdkOptions = SdkOptions(
            url, application_name, auth_key, environment, logging_enabled, log_level, mask_headers, capture
        )
        opts.sanitize()
        is_options_valid = opts.validate()

        if not is_options_valid:
            return

        options = opts

        auto_configuration = ShortLoopAutoConfiguration(opts=opts)
        auto_configuration.init()

        print("ShortLoop Initialized with options: " + str(options))
