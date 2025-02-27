import inspect
import time
from functools import wraps
from typing import (
    Awaitable,
    Callable,
    TypeVar,
    Union,
    cast,
)

from typing_extensions import ParamSpec

from .messages import (
    DEBUG_END_FUNCTION_WORK_MSG,
    DEBUG_START_FUNCTION_WORK_MSG,
    EXCEPTION_MSG,
)
from .protocols import Logger
from .services import get_default_logger, get_signature_repr

P_Spec = ParamSpec('P_Spec')
T_Ret = TypeVar('T_Ret')


def log(
    logger: Union[Logger, None] = None,
    max_arg_value_len: int = 30,
    *,
    include_args: bool = True,
    pretty: bool = True,
) -> Callable[[Callable[P_Spec, T_Ret]], Callable[P_Spec, T_Ret]]:
    """Декоратор для автоматического логирования данных о работе функции."""
    _logger = logger or cast('Logger', get_default_logger())

    def decorator(
        func: Callable[P_Spec, T_Ret],
    ) -> Callable[P_Spec, T_Ret]:
        is_async_function = inspect.iscoroutinefunction(func)

        @wraps(func)
        async def async_wrapper(
            *args: P_Spec.args,
            **kwargs: P_Spec.kwargs,
        ) -> T_Ret:
            time_start = time.perf_counter()
            signature = (
                get_signature_repr(
                    func,
                    max_arg_value_len=max_arg_value_len,
                    args=args,
                    kwargs=kwargs,
                    pretty=pretty,
                )
                if include_args
                else ''
            )
            _log_start_function_work(_logger, func.__name__, signature)
            try:
                result = await cast(Awaitable[T_Ret], func(*args, **kwargs))
            except Exception as exc:
                _log_exception(
                    _logger,
                    func.__name__,
                    exc,
                    signature,
                )
                raise
            else:
                _log_finish_function_work(_logger, func.__name__, signature, time_start)
                return result

        @wraps(func)
        def wrapper(
            *args: P_Spec.args,
            **kwargs: P_Spec.kwargs,
        ) -> T_Ret:
            time_start = time.perf_counter()
            signature = (
                get_signature_repr(
                    func,
                    max_arg_value_len=max_arg_value_len,
                    args=args,
                    kwargs=kwargs,
                    pretty=pretty,
                )
                if include_args
                else ''
            )
            _log_start_function_work(_logger, func.__name__, signature)
            try:
                result = cast(T_Ret, func(*args, **kwargs))
            except Exception as exc:
                _log_exception(
                    _logger,
                    func.__name__,
                    exc,
                    signature,
                )
                raise
            else:
                _log_finish_function_work(_logger, func.__name__, signature, time_start)
                return result

        return (
            cast(Callable[P_Spec, T_Ret], async_wrapper) if is_async_function else wrapper
        )

    return decorator


def _log_exception(
    logger: Logger,
    func_name: str,
    exc: Exception,
    signature: str,
) -> None:
    signature_text = f' с аргументами: {signature}' if signature else ''
    exc_repr = repr(exc)
    logger.error(
        EXCEPTION_MSG.safe_substitute(
            func_name=func_name,
            signature=signature_text,
        ),
        extra={
            'func_name': func_name,
            'exc_repr': exc_repr,
            'signature': signature,
        },
    )


def _log_start_function_work(logger: Logger, func_name: str, signature: str) -> None:
    signature_text = f' с аргументами: {signature}' if signature else ''
    logger.info(
        DEBUG_START_FUNCTION_WORK_MSG.safe_substitute(
            func_name=func_name,
            signature=signature_text,
        ),
        extra={
            'func_name': func_name,
            'signature': signature,
        },
    )


def _log_finish_function_work(
    logger: Logger,
    func_name: str,
    signature: str,
    time_start: float,
) -> None:
    work_time = time.perf_counter() - time_start
    signature_text = f' с аргументами: {signature}' if signature else ''
    logger.info(
        DEBUG_END_FUNCTION_WORK_MSG.safe_substitute(
            func_name=func_name,
            work_time=f'{work_time:.4f}',
            signature=signature_text,
        ),
        extra={
            'func_name': func_name,
            'signature': signature,
            'work_time': work_time,
        },
    )
