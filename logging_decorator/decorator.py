import inspect
import time
from functools import wraps
from typing import (
    Awaitable,
    Callable,
    TypeVar,
    Union,
    cast,
    overload,
)
from typing_extensions import ParamSpec

from .messages import (
    DEBUG_END_FUNCTION_WORK_MSG,
    DEBUG_START_FUNCTION_WORK_MSG,
    EXCEPTION_MSG,
)
from .protocols import Logger
from .services import get_default_logger, get_signature_repr

P_Spec = ParamSpec("P_Spec")
T_Ret = TypeVar("T_Ret")


def log(
    logger: Union[Logger, None] = None,
) -> Callable[[Callable[P_Spec, T_Ret]], Callable[P_Spec, T_Ret]]:
    """Декоратор для автоматического логирования данных о работе функции."""
    _logger = logger or cast(Logger, get_default_logger())

    @overload
    def decorator(
        func: Callable[P_Spec, T_Ret],
    ) -> Callable[P_Spec, T_Ret]:
        ...

    @overload
    def decorator(  # type: ignore
        func: Callable[P_Spec, Awaitable[T_Ret]],
    ) -> Callable[P_Spec, Awaitable[T_Ret]]:
        ...

    def decorator(
        func: Union[Callable[P_Spec, T_Ret], Callable[P_Spec, Awaitable[T_Ret]]],
    ) -> Callable[P_Spec, T_Ret]:
        is_async_function = inspect.iscoroutinefunction(func)

        @wraps(func)
        async def async_wrapper(
            *args: P_Spec.args,
            **kwargs: P_Spec.kwargs,
        ) -> T_Ret:
            time_start = time.perf_counter()
            signature = get_signature_repr(*args, **kwargs)
            _log_start_function_work(_logger, func.__name__, signature)
            try:
                result = await cast(Awaitable[T_Ret], func(*args, **kwargs))
            except Exception as exc:
                _log_exception_with_raise(
                    _logger,
                    func.__name__,
                    exc,
                    signature,
                )
            else:
                _log_finish_function_work(_logger, func.__name__, signature, time_start)
                return result

        @wraps(func)
        def wrapper(
            *args: P_Spec.args,
            **kwargs: P_Spec.kwargs,
        ) -> T_Ret:
            time_start = time.perf_counter()
            signature = get_signature_repr(*args, **kwargs)
            _log_start_function_work(_logger, func.__name__, signature)
            try:
                result = cast(T_Ret, func(*args, **kwargs))
            except Exception as exc:
                _log_exception_with_raise(
                    _logger,
                    func.__name__,
                    exc,
                    signature,
                )
            else:
                _log_finish_function_work(_logger, func.__name__, signature, time_start)
                return result

        return (
            cast(Callable[P_Spec, T_Ret], async_wrapper)
            if is_async_function
            else wrapper
        )

    return decorator


def _log_exception_with_raise(
    logger: Logger,
    func_name: str,
    exc: Exception,
    signature: str,
):
    exc_repr = repr(exc)
    logger.exception(EXCEPTION_MSG.substitute(**locals()))
    raise exc


def _log_start_function_work(logger: Logger, func_name: str, signature: str) -> None:
    logger.info(DEBUG_START_FUNCTION_WORK_MSG.safe_substitute(**locals()))


def _log_finish_function_work(
    logger: Logger,
    func_name: str,
    signature: str,
    time_start: float,
) -> None:
    work_time = time.perf_counter() - time_start
    logger.info(DEBUG_END_FUNCTION_WORK_MSG.substitute(**locals()))
