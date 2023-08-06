import logging
from datetime import datetime
from typing_extensions import Literal
from json_log_formatter import VerboseJSONFormatter

LOGGER_NAME = 'trading-it'


class DatadogJSONFormatter(VerboseJSONFormatter):
    def __init__(self, app_code: str, fmt: str = None, datefmt: str = None, style: Literal["%", "{", "$"] = "%", validate: bool = True) -> None:
        super().__init__(fmt, datefmt, style, validate)
        self.app_code = app_code.lower()

    def json_record(self, message: str, extra: dict, record: logging.LogRecord) -> dict:
        extra['message'] = message

        # Datadog mapped fields
        extra['level'] = record.levelname
        extra['name'] = record.name
        extra['service'] = f'trading-{self.app_code}-api'
        if 'timestamp' not in extra:
            extra['timestamp'] = datetime.utcnow()

        if record.exc_info:
            extra['exc_info'] = self.formatException(record.exc_info)

        return extra


def init_trading_logger(app_code):
    global LOGGER_NAME
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = DatadogJSONFormatter(app_code=app_code)

    ch.setFormatter(formatter)

    logger.addHandler(ch)


def get_trading_logger():
    global LOGGER_NAME
    return logging.getLogger(LOGGER_NAME)
