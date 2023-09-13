import logging
from logging import Logger
from typing import Any


def get_default_logger() -> Logger:
    """Получаем дефолтный логгер."""
    logging.basicConfig(level=logging.DEBUG)
    return logging.getLogger()


def get_signature_repr(*args: Any, **kwargs: Any) -> str:
    """Получаем строковое представление аргументов функции."""
    args_repr = [repr(arg) for arg in args]
    kwargs_repr = [
        f"{kwarg_title}={kwarg_val!r}" for kwarg_title, kwarg_val in kwargs.items()
    ]
    return ", ".join(args_repr + kwargs_repr)
