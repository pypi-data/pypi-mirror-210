import importlib
import logging
import traceback

from tornado.options import options


def sentry_monitor():
    sentry_config = options.sentry_config
    enable = sentry_config.pop("enable", False)
    if enable:
        try:
            sentry_sdk = importlib.import_module("sentry_sdk")
            sentry_sdk_tornado = importlib.import_module("sentry_sdk.integrations.tornado")
        except ImportError:
            raise Exception(f"sentry-sdk is not exist,run:pip install sentry-sdk==1.22.2")
        sentry_config.pop("integrations", "")
        try:
            sentry_sdk.init(
                integrations=[
                    sentry_sdk_tornado.TornadoIntegration(),
                ],
                **sentry_config
            )
        except Exception:
            logging.error(traceback.format_exc())
