import inspect
import time
from functools import wraps
from typing import Awaitable, Callable, TypeVar, cast

from typing_extensions import ParamSpec, Union

from .config import LogConfig
from .protocols import Logger
from .services import get_signature_repr

P = ParamSpec('P')
T = TypeVar('T')
LoggerType = TypeVar('LoggerType', bound='Logger')


def log(  # noqa: C901
    logger: Logger,
    config: Union[LogConfig, None] = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Декоратор для логирования работы функций."""
    config = config or LogConfig()

    def decorator(func: Callable[P, T]) -> Callable[P, T]:  # noqa: C901
        is_async = inspect.iscoroutinefunction(func)

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
            start_time = time.perf_counter()
            _log_start_work(*args, **kwargs)
            try:
                result = await cast(Awaitable[T], func(*args, **kwargs))
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

        return cast(Callable[P, T], async_wrapper if is_async else sync_wrapper)

    return decorator
