import sys
from contextvars import ContextVar
from types import CodeType, FrameType, TracebackType
from typing import (
    Any,
    Awaitable,
    Callable,
    NoReturn,
    Optional,
    ParamSpec,
    Union,
    overload,
)

from exceptions_mapper import DetailedError
from logging_decorator.logging_decorator.config import LogConfig
from logging_decorator.logging_decorator.services import T, get_signature_repr, is_async
from logging_decorator.protocols import SyncOrAsyncFunc

P = ParamSpec('P')
request_context: ContextVar[dict[str, Any]] = ContextVar('request_context', default={})  # noqa: B039


def map_error(  # noqa: C901
    errors: Optional[dict[type[Exception], type[DetailedError]]] = None,
    *,
    exclude_args: set[str] | None = None,
    config: LogConfig | None = None,
) -> SyncOrAsyncFunc:
    """Декоратор для логирования работы функций."""
    config = config or LogConfig()
    errors = errors or {Exception: DetailedError}
    exclude_args = exclude_args or set()

    @overload
    def decorator(func: Callable[P, T]) -> Callable[P, T]: ...

    @overload
    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]: ...

    def decorator(  # type: ignore
        func: Union[Callable[P, T], Callable[P, Awaitable[T]]],
    ) -> Union[Callable[P, T], Callable[P, Awaitable[T]]]:
        def _get_local_vars(frame: FrameType, exclude: set[str]) -> dict[str, Any]:
            """Получает указанные локальные переменные из фрейма."""
            return {
                name: val for name, val in frame.f_locals.items() if name not in exclude
            }

        def _raise_error(
            e: Exception,
            args: tuple[Any, ...],
            kwargs: dict[str, Any],
        ) -> NoReturn:
            details = get_signature_repr(func, args, kwargs, config)
            error_cls = errors.get(type(e), DetailedError)

            context = request_context.get().copy()
            _, _, exc_tb = sys.exc_info()
            frame = _get_error_frame(exc_tb, func.__code__) if exc_tb else None
            context.update({'locals': _get_local_vars(frame, exclude_args)})  # type: ignore
            error = error_cls(
                message=str(e),
                details=details,
                context=context,
            )
            raise error.with_context(
                exception_type=type(e).__name__,
                function_name=func.__name__,
            ) from e

        if is_async(func):

            async def _map_error_async(*args: P.args, **kwargs: P.kwargs) -> T:
                try:
                    result = await func(*args, **kwargs)
                except Exception as e:  # noqa: BLE001
                    # нельзя делать to_thread, т.к. не получится получить traceback exc
                    _raise_error(e, args, kwargs)
                return result

            return _map_error_async

        def _map_error(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                result = func(*args, **kwargs)
            except Exception as e:  # noqa: BLE001
                _raise_error(e, args, kwargs)
            return result  # type: ignore

        return _map_error

    return decorator


def _get_error_frame(exc_tb: TracebackType, func_code: CodeType) -> FrameType | None:
    """Ищет фрейм целевой функции в трассировке исключения."""
    tb = exc_tb
    while tb is not None:
        if tb.tb_frame.f_code == func_code:
            return tb.tb_frame
        tb = tb.tb_next  # type: ignore
    return None
