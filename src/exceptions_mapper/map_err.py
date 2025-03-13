import asyncio
from typing import Any, Awaitable, Callable, ParamSpec, Type, Union, overload

from src.exceptions_mapper.exceptions import DetailedError
from src.logging_decorator import LogConfig
from src.logging_decorator.decorator import T, is_async
from src.logging_decorator.services import get_signature_repr
from src.protocols import SyncOrAsyncFunc

P = ParamSpec('P')


def map_error(  # noqa: C901
    errors: dict[Type[Exception], Type[DetailedError]] | None = None,
) -> SyncOrAsyncFunc:
    """Декоратор для логирования работы функций."""
    errors = errors or {Exception: DetailedError}

    @overload
    def decorator(func: Callable[P, T]) -> Callable[P, T]: ...

    @overload
    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]: ...

    def decorator(  # type: ignore
        func: Union[Callable[P, T], Callable[P, Awaitable[T]]],
    ) -> Union[Callable[P, T], Callable[P, Awaitable[T]]]:
        def _raise_error(
            e: Exception,
            args: tuple[Any, ...],
            kwargs: dict[str, Any],
        ) -> None:  # noqa: ANN401
            details = get_signature_repr(
                func,
                args,
                kwargs,
                LogConfig(),
            )
            raise errors.get(type(e), DetailedError)(
                message=str(e),
                details=details,
            ) from e

        if is_async(func):

            async def _map_error_async(*args: P.args, **kwargs: P.kwargs) -> T:  # type: ignore
                try:
                    result = await func(*args, **kwargs)
                except Exception as e:  # noqa: BLE001
                    await asyncio.to_thread(_raise_error, e, args, kwargs)
                else:
                    return result

            return _map_error_async

        def _map_error(*args: P.args, **kwargs: P.kwargs) -> T:  # type: ignore
            try:
                result = func(*args, **kwargs)
            except Exception as e:  # noqa: BLE001
                _raise_error(e, args, kwargs)
            else:
                return result  # type: ignore

        return _map_error

    return decorator
