import asyncio
import inspect
import time
from functools import wraps
from typing import (
    Awaitable,
    Callable,
    ParamSpec,
    TypeGuard,
    TypeVar,
    Union,
    overload,
)

from src.protocols import Logger, SyncOrAsyncFunc

from .config import LogConfig
from .pretty_repr import pretty_repr
from .services import get_signature_repr

P = ParamSpec('P')
T = TypeVar('T')
LoggerType = TypeVar('LoggerType', bound='Logger')


def log(  # type: ignore # noqa: C901
    logger: Logger,
    config: Union[LogConfig, None] = None,
) -> SyncOrAsyncFunc:
    """Декоратор для логирования работы функций."""
    config = config or LogConfig()

    @overload
    def decorator(func: Callable[P, T]) -> Callable[P, T]: ...

    @overload
    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]: ...

    def decorator(  # type: ignore # noqa: C901
        func: Union[Callable[P, T], Callable[P, Awaitable[T]]],
    ) -> Union[Callable[P, T], Callable[P, Awaitable[T]]]:
        def _log_start_work(*args: P.args, **kwargs: P.kwargs) -> float:
            start = time.perf_counter()
            signature_repr = get_signature_repr(func, args, kwargs, config)
            signature = ''
            if config.include_args and signature_repr:
                signature = f' с аргументами:\n  {signature_repr}'
            msg = f'Функция "{func.__name__}" начала работу{signature}.'
            logger.info(
                msg,
                extra={
                    'func': func.__name__,
                    'arguments': signature,
                    'status': 'start',
                },
            )
            return start

        def _log_exception(exc: Exception) -> None:
            exc_repr = pretty_repr(
                exc,
                LogConfig(
                    max_depth=max(2, config.max_depth),  # увеличиваем глубину
                    max_arg_length=config.max_arg_length,
                    include_args=config.include_args,
                    show_types=config.show_types,
                    skipped_args=config.skipped_args,
                ),
            )
            msg = f'Ошибка в функции "{func.__name__}":\n{exc_repr}.'
            logger.exception(  # noqa: LOG004
                msg,
                extra={
                    'func': func.__name__,
                    'exception': exc_repr,
                    'status': 'error',
                },
            )

        def _log_finish_work(start_time: float) -> None:
            elapsed = time.perf_counter() - start_time
            msg = f'Функция "{func.__name__}" завершила работу за {elapsed:.4f} сек.'
            logger.info(
                msg,
                extra={
                    'func': func.__name__,
                    'elapsed': elapsed,
                    'status': 'success',
                },
            )

        if is_async(func):

            @wraps(func)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                """Обертка для асинхронных функций."""
                start_time = await asyncio.to_thread(_log_start_work, *args, **kwargs)
                try:
                    result = await func(*args, **kwargs)
                except Exception as exc:
                    await asyncio.to_thread(_log_exception, exc)
                    raise
                else:
                    await asyncio.to_thread(_log_finish_work, start_time)
                    return result

            return async_wrapper

        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            """Обертка для синхронных функций."""
            start_time = _log_start_work(*args, **kwargs)
            try:
                result = func(*args, **kwargs)
            except Exception as exc:
                _log_exception(exc)
                raise
            else:
                _log_finish_work(start_time)
                return result  # type: ignore

        return sync_wrapper

    return decorator  # type: ignore


def is_async(
    func: Union[Callable[P, T], Callable[P, Awaitable[T]]],
) -> TypeGuard[Callable[P, Awaitable[T]]]:
    """Проверяет, является ли функция асинхронной."""
    return inspect.iscoroutinefunction(func)
