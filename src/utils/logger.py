# stdlib
import datetime
import json
import logging.handlers
import os
import time
from typing import Any, Dict

# thirdparty
import psutil
from flask import g
from pythonjsonlogger import jsonlogger

logger = logging.getLogger("utils-logger")


class ExtraLoggerAdapter(logging.LoggerAdapter):
    """
    Декоратор для логгера, добавляет extra безусловно для всех лог-записей.

    Пример использования:
    logger = ExtraLoggerAdapter(logger, extra={"new_extra_field": "value_extra_field"})

    logger.error("New log record")
    """

    def process(self, msg, kwargs):
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        kwargs["extra"].update(self.extra)
        return msg, kwargs


def set_extra_for_logs(extra_dict: Dict):
    """
    Добавляет во все логгеры в рамках текущего треда доп. информацию

    Пример:
    set_extra_for_logs({"module_name": "heavy_calculate"})

    # тут в extra будет автоматически добавлен module_name
    logger.error("Произошла ошибка расчета")
    """
    try:
        g.setdefault("extra_info_for_logs", {})
        g.extra_info_for_logs.update(extra_dict)
    except RuntimeError:
        logger.error("Некорректная работа с объектом flask.g", exc_info=True)


class KibanaAdapterJsonFormatter(jsonlogger.JsonFormatter):
    """
    Форматтер, для добавления поля msg в выходной json. текущий стек парсит только такие логи
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_proc = psutil.Process(os.getpid())

    def _get_memory_used_md(self):
        return self._current_proc.memory_info().rss / 1024 ** 2

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        log_record["msg"] = log_record["message"]  # Решение для корректного парсинга логов кибаной
        del log_record["message"]

        log_record["logger"] = {}
        log_record["logger"]["name"] = record.name
        log_record["logger"]["level"] = record.levelname
        log_record["logger"]["time"] = datetime.datetime.fromtimestamp(time.time()).isoformat()

        log_record["debug_info"] = {}
        log_record["debug_info"]["memory_used_total"] = round(self._get_memory_used_md(), 2)

        try:
            # расход памяти от начала обработки запроса/команды
            if "debug_first_log_memory_used" in g:
                log_record["debug_info"]["memory_used_first_log"] = round(
                    self._get_memory_used_md() - g.debug_first_log_memory_used, 2
                )
            g.setdefault("debug_first_log_memory_used", self._get_memory_used_md())

            # расход памяти от предыдущей лог-записи
            if "debug_last_log_memory_used" in g:
                log_record["debug_info"]["memory_used_last_log"] = round(
                    self._get_memory_used_md() - g.debug_last_log_memory_used, 2
                )
            g.debug_last_log_memory_used = self._get_memory_used_md()

            # количество секунд от начала обработки
            if "debug_first_log_time_estimate" in g:
                log_record["debug_info"]["seconds_from_first_log"] = round(
                    time.time() - g.debug_first_log_time_estimate, 2
                )
            g.setdefault("debug_first_log_time_estimate", time.time())

            # количество секунд от предыдущей лог-записи
            if "debug_last_log_time_estimate" in g:
                log_record["debug_info"]["seconds_from_last_log"] = round(
                    time.time() - g.debug_last_log_time_estimate, 2
                )
            g.debug_last_log_time_estimate = time.time()

            # log_record["thread_name"]
            if record.threadName != "MainThread":
                log_record["thread_name"] = record.threadName

            # добавляем информацию о ДО (только если она есть)
            if "global_filter" in g:
                field_name = g.global_filter.field_name
                log_record["field_name"] = field_name

            if "extra_info_for_logs" in g:
                extra_info = g.extra_info_for_logs
                log_record.update(extra_info)
        except RuntimeError:
            pass


class ExtraFormatter(KibanaAdapterJsonFormatter):
    COMMON_RECORD_ATTRS = [
        "args",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "linenno",
        "lineno",
        "message",
        "module",
        "msecs",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack",
        "tags",
        "thread",
        "threadName",
        "stack_info",
        "asctime",
        "extra",
        "extra_info",
        "report",
    ]

    def serialize_log_record(self, log_record: Dict[str, Any]) -> str:
        """
        Необходимо переопределить этот метод таким образом, чтобы не происходила
        сериализация в json строку. Костыль.
        """
        return log_record

    def format(self, record):
        s = super().format(record)

        message = (
            datetime.datetime.fromtimestamp(record.created).strftime("%H:%M:%S.%f")
            + " "
            + s["msg"]
        )
        # добавляем отладочную информацию в лог запись
        message += "\ndebug_info:{0}".format(
            json.dumps(s["debug_info"], ensure_ascii=False, indent=1, default=str)
        )
        # добавляем extra поля
        extra = {k: v for k, v in record.__dict__.items() if k not in self.COMMON_RECORD_ATTRS}
        if extra:
            message += "\nextra:{0}".format(
                json.dumps(extra, ensure_ascii=False, indent=1, default=str)
            )

        return message
