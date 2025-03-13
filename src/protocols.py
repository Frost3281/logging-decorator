from typing import Any, Awaitable, Callable, ParamSpec, Protocol, TypeVar, Union, overload


class Logger(Protocol):
    """Протокол логгера."""

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """Сообщение в уровне инфо."""

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """Сообщение в уровне исключения."""


P = ParamSpec('P')
T = TypeVar('T')


class SyncOrAsyncFunc(Protocol):
    """Типизированный протокол для декорирования функций."""

    @overload
    def __call__(self, func: Callable[P, T]) -> Callable[P, T]: ...

    @overload
    def __call__(self, func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]: ...

    def __call__(  # type: ignore
        self,
        func: Union[Callable[P, T], Callable[P, Awaitable[T]]],
    ) -> Union[Callable[P, T], Callable[P, Awaitable[T]]]:
        """Синхронная или асинхронная функция."""
