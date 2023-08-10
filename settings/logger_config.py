# stdlib
from copy import deepcopy

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json_formatter": {
            "()": "src.utils.logger.KibanaAdapterJsonFormatter",
            "json_ensure_ascii": False,
        },
        "extended_formatter": {
            "()": "src.utils.logger.ExtraFormatter",
        },
    },
    "handlers": {
        "console_json_handler": {
            "class": "logging.StreamHandler",
            "formatter": "json_formatter",
            "stream": "ext://sys.stdout",
        },
        "json_file_handler": {
            "class": "logging.handlers.WatchedFileHandler",
            "formatter": "json_formatter",
            "filename": "logs/app.json",
            "encoding": "utf8",
        },
        "console_extended_handler": {
            "class": "logging.StreamHandler",
            "formatter": "extended_formatter",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "level": "INFO",
        # хендлеры устанавливаются далее в функциях
        "handlers": [],
    },
    "loggers": {
        # отключаем спам логами при генерации данных factoryboy
        "factory": {"level": "WARN"},
        "factory.generate": {"level": "WARN"},
        "faker.factory": {"level": "WARN"},
    },
}


def get_raw_output_logging_config():
    logger_config = deepcopy(LOGGING_CONFIG)
    logger_config["root"]["handlers"].append("console_extended_handler")
    logger_config["root"]["handlers"].append("json_file_handler")
    return logger_config


def get_json_output_logging_config():
    logger_config = deepcopy(LOGGING_CONFIG)
    logger_config["root"]["handlers"].append("console_json_handler")
    return logger_config
