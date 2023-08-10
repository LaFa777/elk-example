# stdlib
import logging
import logging.config
import threading

# thirdparty
from celery.signals import setup_logging

# project
from settings.base import *  # noqa
from settings.logger_config import get_json_output_logging_config

logging.config.dictConfig(get_json_output_logging_config())

# Для обработки всех сообщений из модуля warnings модулем logging
# (а соответственно и выводом в json и в кибане)
logging.captureWarnings(True)

# обработка всех логов для celery
@setup_logging.connect
def setup_logging(**_kwargs):
    logging.config.dictConfig(get_json_output_logging_config())


def excepthook(args):
    """
    Если произошла ошибка в тредах и поднялась до сюда, то это критикал.
    Нужно звонить во все колокола.
    """
    # stdlib
    import logging

    logger = logging.getLogger("critical_thread_exception")
    logger.critical("Завершение треда с критической ошибкой", exc_info=True)


threading.excepthook = excepthook
