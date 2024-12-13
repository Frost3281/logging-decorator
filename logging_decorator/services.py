import logging
from logging import Logger
from typing import Any


def get_default_logger() -> Logger:
    """Получаем дефолтный логгер."""
    logging.basicConfig(level=logging.DEBUG)
    return logging.getLogger()


def get_signature_repr(*args: Any, **kwargs: Any) -> str:  # noqa: ANN401
    """Получаем строковое представление аргументов функции, сокращая длинные аргументы."""

    def shorten(value: Any) -> str:  # noqa: ANN401
        """Сокращаем строку до заданной длины с добавлением '...'."""
        max_arg_value_len = 30
        string_repr = repr(value)
        if len(string_repr) > max_arg_value_len:
            return string_repr[: max_arg_value_len - 3] + '...'
        return string_repr

    args_repr = [shorten(arg) for arg in args]
    kwargs_repr = [
        f'{kwarg_title}={shorten(kwarg_val)}' for kwarg_title, kwarg_val in kwargs.items()
    ]
    return ', '.join(args_repr + kwargs_repr)
