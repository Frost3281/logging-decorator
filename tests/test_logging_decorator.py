import asyncio
from typing import Awaitable, Callable, Union, get_type_hints

import pytest

from logging_decorator import log
from logging_decorator.messages import (
    DEBUG_END_FUNCTION_WORK_MSG,
    DEBUG_START_FUNCTION_WORK_MSG,
    EXCEPTION_MSG,
)
from tests.conftest import MockLogger
from tests.services import check_msg_from_list_contains_text

T_SyncFunction = Callable[[int, str], str]
T_AsyncFunction = Callable[[int, str], Awaitable[str]]
T_AsyncOrSyncFunction = Union[T_SyncFunction, T_AsyncFunction]


def sync_func_logging_testing(arg1: int, arg2: str) -> str:
    return f"{arg1} {arg2}"


async def async_func_logging_testing(arg1: int, arg2: str) -> str:
    return f"{arg1} {arg2}"


SYNC_FUNC_NAME = sync_func_logging_testing.__name__
ASYNC_FUNC_NAME = async_func_logging_testing.__name__


@pytest.mark.parametrize(
    'function', [sync_func_logging_testing, async_func_logging_testing],
)
def test_sync_func_decorator_type_hinting(function: T_AsyncOrSyncFunction):
    func_annotations = get_type_hints(function)
    deco_annotations = get_type_hints(log()(function))
    assert func_annotations == deco_annotations


@pytest.mark.parametrize(
    'function,func_name,wrapper',
    [
        [sync_func_logging_testing, SYNC_FUNC_NAME, lambda func: func],
        [async_func_logging_testing, ASYNC_FUNC_NAME, asyncio.run],
    ]
)
def test_sync_function_logs_start_and_end(
    function: T_AsyncOrSyncFunction,
    func_name: str,
    mock_logger: MockLogger,
    wrapper: Callable[[T_AsyncOrSyncFunction], T_SyncFunction],
):
    decorated = log(mock_logger)(function)
    result = wrapper(decorated(10, "abc"))  # type: ignore
    assert result == "10 abc"
    assert check_msg_from_list_contains_text(
        DEBUG_START_FUNCTION_WORK_MSG.substitute(
            func_name=func_name, signature="10, 'abc'"
        ),
        mock_logger.logged_messages,
    )
    with pytest.raises(KeyError):
        DEBUG_END_FUNCTION_WORK_MSG.substitute(
            func_name=func_name, signature="10, 'abc'"
        )
    assert check_msg_from_list_contains_text(
        DEBUG_END_FUNCTION_WORK_MSG.safe_substitute(
            func_name=func_name, signature="10, 'abc'"
        ).split("$")[0],
        mock_logger.logged_messages,
    )


@pytest.mark.parametrize(
    'function,func_name,wrapper',
    [
        [sync_func_logging_testing, SYNC_FUNC_NAME, lambda func: func],
        [async_func_logging_testing, ASYNC_FUNC_NAME, asyncio.run],
    ]
)
def test_sync_function_logs_exception(
    function: T_AsyncOrSyncFunction,
    func_name: str,
    wrapper: Callable[[T_AsyncOrSyncFunction], T_SyncFunction],
    mock_logger: MockLogger,
):
    decorated = log(mock_logger)(function)
    with pytest.raises(TypeError):
        wrapper(decorated(10, "", None))  # type: ignore
    assert check_msg_from_list_contains_text(
        EXCEPTION_MSG.safe_substitute(func_name=func_name).split("$")[0],
        mock_logger.logged_messages,
    )
    assert check_msg_from_list_contains_text("TypeError", mock_logger.logged_messages)
