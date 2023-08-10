# stdlib
import logging.config

# project
from settings.base import *  # noqa
from settings.logger_config import get_raw_output_logging_config

DEBUG = True

logging.config.dictConfig(get_raw_output_logging_config())

# для импорта локальной конфигурации
try:
    # project
    from settings.local import *  # noqa
except Exception:
    pass
