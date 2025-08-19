from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Awaitable, Callable, TypeVar, get_type_hints

import pytest
from typing_extensions import ParamSpec

from logging_decorator.logging_decorator import log
from logging_decorator.logging_decorator.config import LogConfig
from logging_decorator.logging_decorator.services import get_signature_repr

if TYPE_CHECKING:
    from tests.conftest import MockLogger


P = ParamSpec('P')
T = TypeVar('T')
AsyncFunc = Callable[P, Awaitable[T]]
SyncFunc = Callable[P, T]


@dataclass
class TestCase:
    """Датакласс для хранения параметров тест-кейса."""

    name: str
    func: Callable[..., Any]
    is_async: bool
    include_args: bool


def sync_example(a: int, b: str) -> str:
    """Синхронная тестовая функция."""
    return f'{a}-{b}'


async def async_example(a: int, b: str) -> str:
    """Асинхронная тестовая функция."""
    return f'{a}-{b}'


TEST_CASES = [
    TestCase(
        name='Синхронная функция с аргументами',
        func=sync_example,
        is_async=False,
        include_args=True,
    ),
    TestCase(
        name='Асинхронная функция без аргументов',
        func=async_example,
        is_async=True,
        include_args=False,
    ),
]


@pytest.mark.parametrize('case', TEST_CASES, ids=lambda x: x.name)
def test_type_hints_preserved(case: TestCase, logger: MockLogger) -> None:
    """Тест сохранения аннотаций типов после декорирования."""
    original_hints = get_type_hints(case.func)
    decorated = log(config=LogConfig(), logger=logger)(case.func)
    decorated_hints = get_type_hints(decorated)
    assert original_hints == decorated_hints, 'Аннотации типов должны совпадать'


@pytest.mark.parametrize('case', TEST_CASES, ids=lambda x: x.name)
def test_function_logging(case: TestCase, logger: MockLogger) -> None:
    """Тест корректности логирования работы функции."""
    config = LogConfig(include_args=case.include_args, max_arg_length=50)
    decorated = log(logger=logger, config=config)(case.func)

    if case.is_async:
        result = asyncio.run(decorated(10, 'test'))  # type: ignore
    else:
        result = decorated(10, 'test')  # type: ignore

    expected = '10-test'
    assert result == expected, 'Некорректный результат выполнения'

    assert len(logger.messages) >= 2, 'Должно быть минимум два сообщения'

    start_msg = logger.messages[0]
    assert 'начала работу' in start_msg['msg'], 'Отсутствует сообщение о старте'

    end_msg = logger.messages[-1]
    assert 'завершила работу' in end_msg['msg'], 'Отсутствует сообщение о завершении'


_VALUE_ERROR_MSG = "ValueError('Тестовая ошибка')."


def test_exception_logging(
    *,
    logger: MockLogger,
) -> None:
    """Тест логирования исключений."""

    @log(logger=logger, config=LogConfig(show_complex_args=False))
    def faulty_func() -> None:
        msg = 'Тестовая ошибка'
        raise ValueError(msg)

    with pytest.raises(ValueError, match='Тестовая ошибка'):
        faulty_func()

    error_msg = logger.messages[-1]
    assert error_msg['level'] == 'ERROR', 'Должно быть сообщение об ошибке'
    assert error_msg['msg'] == f'Ошибка в функции "faulty_func":\n{_VALUE_ERROR_MSG}'


@pytest.mark.parametrize(
    ('skipped_args', 'expected_repr'),
    [
        ((), "a: int = 42\n  b: str = 'value'"),
        (('b',), 'a: int = 42'),
        (('a',), "b: str = 'value'"),
    ],
)
def test_signature_repr(skipped_args: tuple[str, ...], expected_repr: str) -> None:
    """Тест формирования представления сигнатуры функции."""

    def sample_func(a: int, b: str = 'test') -> None: ...

    args = (42,)
    kwargs = {'b': 'value'}
    signature = get_signature_repr(
        sample_func,
        args,
        kwargs,
        config=LogConfig(skipped_args=skipped_args),
    )
    assert signature == expected_repr, 'Некорректное представление аргументов'


def test_function_signature_repr() -> None:
    """Тест формирования представления сигнатуры функции."""

    def inner_func(a: str) -> None: ...

    async def sample_func(a: int, func: Callable[[str], None], b: str = 'ts') -> None: ...

    signature = get_signature_repr(
        sample_func,
        (42, inner_func),
        {'b': 'value'},
        config=LogConfig(),
    )
    expected = (
        "a: int = 42\n  func: function = inner_func(a: str) -> None\n  b: str = 'value'"
    )
    assert signature == expected
