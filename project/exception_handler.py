from urllib.error import HTTPError
from dateutil.parser import ParserError
import logging
from flask import make_response
from functools import wraps
from werkzeug.exceptions import HTTPException


def handle_exception(logger: logging.Logger):
    """
        Декоратор, который оборачивает функцию в блок обработки исключений
    """
    def decorator(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except ParserError as e:
                return logAndReturnError(logger, str(e), 400)
            except ValueError as e:
                return logAndReturnError(logger, str(e), 400)
            except HTTPException as e:
                if e.code == 404:
                    return logAndReturnError(logger, "Категория/товар не найден.", 404)
            except Exception as e:
                return logAndReturnError(logger, str(e), 400)

        return wrap

    return decorator

def logAndReturnError(logger: logging.Logger, message: str, status: int):
    """
        Логирует ошибку и возвращает сообщение об ошибке и статус код
    """
    logger.exception(message)
    return make_response(message, status)