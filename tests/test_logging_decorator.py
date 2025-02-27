import asyncio
from typing import Awaitable, Callable, Union, get_type_hints

import pytest

from logging_decorator import log
from logging_decorator.messages import (
    DEBUG_END_FUNCTION_WORK_MSG,
    DEBUG_START_FUNCTION_WORK_MSG,
    EXCEPTION_MSG,
)
from logging_decorator.services import get_signature_repr
from tests.conftest import MockLogger
from tests.services import check_msg_from_list_contains_text

T_SyncFunction = Callable[[int, str], str]
T_AsyncFunction = Callable[[int, str], Awaitable[str]]
T_AsyncOrSyncFunction = Union[T_SyncFunction, T_AsyncFunction]


def sync_func_logging_testing(arg1: int, arg2: str) -> str:
    return f'{arg1} {arg2}'


async def async_func_logging_testing(arg1: int, arg2: str) -> str:
    return f'{arg1} {arg2}'


SYNC_FUNC_NAME = sync_func_logging_testing.__name__
ASYNC_FUNC_NAME = async_func_logging_testing.__name__


@pytest.mark.parametrize(
    'function',
    [sync_func_logging_testing, async_func_logging_testing],
)
def test_sync_func_decorator_type_hinting(function: T_AsyncOrSyncFunction):
    func_annotations = get_type_hints(function)
    deco_annotations = get_type_hints(log()(function))
    assert func_annotations == deco_annotations


@pytest.mark.parametrize(
    ('function', 'func_name', 'wrapper', 'include_args'),
    [
        (sync_func_logging_testing, SYNC_FUNC_NAME, lambda func: func, True),
        (async_func_logging_testing, ASYNC_FUNC_NAME, asyncio.run, False),
    ],
)
def test_function_job_log(
    function: T_AsyncOrSyncFunction,
    func_name: str,
    mock_logger: MockLogger,
    include_args: bool,  # noqa: FBT001
    wrapper: Callable[[T_AsyncOrSyncFunction], T_SyncFunction],
):
    decorated = log(mock_logger, include_args=include_args)(function)
    result = wrapper(decorated(10, 'abc'))  # type: ignore
    assert result == '10 abc'
    signature = (
        get_signature_repr(function, args=(10, 'abc'), kwargs={}) if include_args else ''
    )
    assert check_msg_from_list_contains_text(
        DEBUG_START_FUNCTION_WORK_MSG.substitute(
            func_name=func_name,
            signature=f' с аргументами: {signature}' if include_args else '',
        ),
        mock_logger.logged_messages,
    )
    assert check_msg_from_list_contains_text(
        DEBUG_END_FUNCTION_WORK_MSG.safe_substitute(
            func_name=func_name,
            signature="10, 'abc'",
        ).split('$')[0],
        mock_logger.logged_messages,
    )


@pytest.mark.parametrize(
    ('function', 'func_name', 'wrapper'),
    [
        (sync_func_logging_testing, SYNC_FUNC_NAME, lambda func: func),
        (async_func_logging_testing, ASYNC_FUNC_NAME, asyncio.run),
    ],
)
def test_exception_logging(
    function: T_AsyncOrSyncFunction,
    func_name: str,
    wrapper: Callable[[T_AsyncOrSyncFunction], T_SyncFunction],
    mock_logger: MockLogger,
):
    """Тестируем логирование ошибки."""
    decorated = log(mock_logger)(function)
    with pytest.raises(TypeError):
        wrapper(decorated(10, '', None))  # type: ignore
    signature = get_signature_repr(function, args=(10, '', None), kwargs={})
    assert check_msg_from_list_contains_text(
        EXCEPTION_MSG.safe_substitute(func_name=func_name, signature=signature).split(
            '$',
        )[0],
        mock_logger.logged_messages,
    )
    assert check_msg_from_list_contains_text('TypeError', mock_logger.logged_messages)
