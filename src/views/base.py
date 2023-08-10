# stdlib
import logging

# thirdparty
import pydantic
from flask import make_response, request

# project
from src import exceptions
from src.views import schemas

logger = logging.getLogger("apps.elk.views")


def hello_world():
    try:
        params = schemas.HelloSchema(**request.args)
    except pydantic.ValidationError:
        raise exceptions.ViewException(message="Ошибка в переданных параметрах", code=400)

    # вызываем ошибку
    if params.who == "error":
        try:
            1 / 0
        except ZeroDivisionError:
            logger.error("Произошла ошибка деления на 0", exc_info=True, extra={"who": params.who})

    # обычное логгирование
    if params.who == "world":
        msg = "Ты такой оригинальный... придумай что нибудь другое"
        logger.warn(msg, exc_info=True, extra={"who": params.who})
        return msg, 400

    response = make_response(f"Hello {params.who}!", 200)
    response.mimetype = "text/plain"
    return response


def favicon():
    return "Сегодня без favicon.ico", 204
