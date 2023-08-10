# stdlib
import logging

# thirdparty
from flask import Blueprint, current_app, request

# project
from src import exceptions, views
from src.views import schemas

logger = logging.getLogger("apps.elk")

elk_routes = Blueprint("elk_routes", __name__)


def _get_error(logger: logging.Logger, msg: str, code: int):
    """
    Формирует ответ в случае возникновения исключения

    :param msg: Описание ошибки
    :param code: код ответа
    """
    logger.error(
        msg,
        exc_info=True,
        extra={"path": request.path},
    )
    schema = schemas.ErrorResponseSchema(code=code, message=msg)
    return schema.dict(), code


def error_hanler(logger: logging.Logger):
    """
    Обрабатываем возникновение исключения класса ViewException в view.
    Логгирует ошибку и возвращает обобщенный ответ.
    """
    logger = logger

    def wrapped_func(error):
        # для ДЕВ окружения возвращаем ошибку как есть
        if current_app.config["DEBUG"]:
            raise error

        message = getattr(error, "message", "Произошла ошибка на сервере")
        code = 400
        if isinstance(error, exceptions.ViewException):
            code = getattr(error, "code", 400)
        return _get_error(logger, message, code)

    return wrapped_func


elk_routes.app_errorhandler(Exception)(error_hanler(logger))

elk_routes.add_url_rule("/favicon.ico", view_func=views.favicon)
elk_routes.add_url_rule("/elk/hello_world", view_func=views.hello_world)
