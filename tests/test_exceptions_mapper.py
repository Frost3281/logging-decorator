import re
from typing import Any, Awaitable, Callable, NoReturn, Union

import pytest

from exceptions_mapper import DetailedError, map_error
from logging_decorator.logging_decorator.decorator import is_async


class _ZeroDivisionMappedError(DetailedError):
    """Ошибка деления на ноль."""


@map_error(
    {Exception: DetailedError, ZeroDivisionError: _ZeroDivisionMappedError},
    local_params_to_add={'msg'},
)
def _func_test(a: int) -> None:
    """Тестовая функция."""
    if a:
        msg = 'Тестовая ошибка ' + str(a)
        raise ValueError(msg)
    raise ZeroDivisionError


@map_error(
    {Exception: DetailedError, ZeroDivisionError: _ZeroDivisionMappedError},
    local_params_to_add={'msg'},
)
async def _func_test_async(a: int) -> None:
    """Тестовая асинхронная функция."""
    if a:
        msg = 'Тестовая ошибка ' + str(a)
        raise ValueError(msg)
    raise ZeroDivisionError


def _func_test_not_decorated(a: int) -> None:
    """Тестовая функция."""
    _func_test(a)


async def _func_test_async_not_decorated(a: int) -> None:
    """Тестовая асинхронная функция."""
    await _func_test_async(a)


@pytest.mark.parametrize('f', [_func_test, _func_test_async])
@pytest.mark.asyncio
async def test_map_error_with_parameter(f: Callable[..., Union[Any, Awaitable[Any]]]):
    """Тестирование функции map_error."""
    await _check_is_raise(f, DetailedError, 'a: int = 1', 'Тестовая ошибка 1')
    with pytest.raises(AssertionError, match='Regex pattern did not match.'):
        await _check_is_raise(f, DetailedError, 'a: int = 1', 'Тестовая ошибка 2')


@pytest.mark.parametrize('f', [_func_test, _func_test_async])
@pytest.mark.asyncio
async def test_map_error_with_parameter_multiple_exceptions(
    f: Callable[..., Union[Any, Awaitable[Any]]],
):
    """Тестирование функции map_error."""
    await _check_is_raise(f, _ZeroDivisionMappedError, 'Ошибка деления на ноль', arg=0)


@pytest.mark.parametrize('f', [_func_test_async_not_decorated, _func_test_not_decorated])
@pytest.mark.asyncio
async def test_map_error_with_parameter_not_decorated(
    f: Callable[..., Union[Any, Awaitable[Any]]],
):
    """Тестирование функции map_error."""
    f = map_error()(f)
    await _check_is_raise(f, DetailedError, 'a: int = 1')


def test_function_with_raise_detailed_error():
    """Тестирование DetailedError."""

    def raise_function(_: int = 2) -> NoReturn:
        a = 1
        raise DetailedError(message=f'test {a}')

    with pytest.raises(DetailedError) as exc_info:
        raise_function()
    assert exc_info.value.context['args'] == {'_': 2}
    assert exc_info.value.context['locals'] == {'a': 1}


async def _check_is_raise(
    f: Callable[..., Union[Any, Awaitable[Any]]],
    error: type[DetailedError],
    *matches: str,
    arg: int = 1,
) -> None:
    regex_pattern = ''
    for match in matches:
        escaped = re.escape(match)
        regex_pattern += f'(?=.*{escaped})'
    regex_pattern += '.*'
    with pytest.raises(error, match=regex_pattern):
        await f(arg) if is_async(f) else f(arg)  # type: ignore
