import inspect
import time
from functools import wraps
from typing import Awaitable, Callable, TypeVar

from typing_extensions import ParamSpec, TypeGuard, Union

from .config import LogConfig
from .exceptions import WrongFunctionTypeError
from .protocols import Logger
from .services import get_signature_repr

P = ParamSpec('P')
T = TypeVar('T')
LoggerType = TypeVar('LoggerType', bound='Logger')


def log(  # noqa: C901
    logger: Logger,
    config: Union[LogConfig, None] = None,
) -> Callable[
    [Union[Callable[P, T], Callable[P, Awaitable[T]]]],
    Union[Callable[P, T], Callable[P, Awaitable[T]]],
]:
    """Декоратор для логирования работы функций."""
    config = config or LogConfig()

    def decorator(  # noqa: C901
        func: Union[Callable[P, T], Callable[P, Awaitable[T]]],
    ) -> Union[Callable[P, T], Callable[P, Awaitable[T]]]:
        def _log_start_work(*args: P.args, **kwargs: P.kwargs) -> None:
            signature_repr = get_signature_repr(func, args, kwargs, config)
            if config.include_args and signature_repr:
                signature = f' с аргументами:\n  {signature_repr}'
            else:
                signature = ''
            msg = f'Функция "{func.__name__}" начала работу{signature}.'
            logger.info(
                msg,
                extra={
                    'func': func.__name__,
                    'arguments': signature,
                    'status': 'start',
                },
            )

        def _log_exception(exc: Exception) -> None:
            msg = f'Ошибка в функции "{func.__name__}": {repr(exc)}.'
            logger.exception(  # noqa: LOG004
                msg,
                extra={
                    'func': func.__name__,
                    'exception': exc,
                    'status': 'error',
                },
            )

        def _log_finish_work(elapsed: float) -> None:
            msg = f'Функция "{func.__name__}" завершила работу за {elapsed:.4f} сек.'
            logger.info(
                msg,
                extra={
                    'func': func.__name__,
                    'elapsed': elapsed,
                    'status': 'success',
                },
            )

        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            """Обертка для асинхронных функций."""
            if not is_async(func):  # для mypy
                raise WrongFunctionTypeError(should_be_async=True)
            start_time = time.perf_counter()
            _log_start_work(*args, **kwargs)
            try:
                result = await func(*args, **kwargs)
            except Exception as exc:
                _log_exception(exc)
                raise
            else:
                elapsed = time.perf_counter() - start_time
                _log_finish_work(elapsed)
                return result

        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            """Обертка для синхронных функций."""
            if not is_sync(func):  # для mypy
                raise WrongFunctionTypeError(should_be_async=False)
            start_time = time.perf_counter()
            _log_start_work(*args, **kwargs)
            try:
                result = func(*args, **kwargs)
            except Exception as exc:
                _log_exception(exc)
                raise
            else:
                elapsed = time.perf_counter() - start_time
                _log_finish_work(elapsed)
                return result

        return async_wrapper if is_async(func) else sync_wrapper

    return decorator


def is_async(
    func: Union[Callable[P, T], Callable[P, Awaitable[T]]],
) -> TypeGuard[Callable[P, Awaitable[T]]]:
    """Проверяет, является ли функция асинхронной."""
    return inspect.iscoroutinefunction(func)


def is_sync(
    func: Union[Callable[P, T], Callable[P, Awaitable[T]]],
) -> TypeGuard[Callable[P, T]]:
    """Проверяет, является ли функция синхронной."""
    return not is_async(func)
