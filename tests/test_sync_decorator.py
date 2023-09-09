from typing import get_type_hints

import pytest

from logging_decorator import log
from logging_decorator.messages import (
    DEBUG_END_FUNCTION_WORK_MSG,
    DEBUG_START_FUNCTION_WORK_MSG,
    EXCEPTION_MSG,
)
from tests.conftest import MockLogger
from tests.services import check_msg_from_list_contains_text


def sync_func_logging_testing(arg1: int, arg2: str) -> str:
    return f"{arg1} {arg2}"


FUNC_NAME = sync_func_logging_testing.__name__


def test_sync_func_decorator_type_hinting():
    func_annotations = get_type_hints(sync_func_logging_testing)
    deco_annotations = get_type_hints(log()(sync_func_logging_testing))
    assert func_annotations == deco_annotations


def test_sync_function_logs_start_and_end(mock_logger: MockLogger):
    decorated = log(mock_logger)(sync_func_logging_testing)
    result = decorated(10, "abc")
    assert result == "10 abc"
    assert check_msg_from_list_contains_text(
        DEBUG_START_FUNCTION_WORK_MSG.substitute(
            func_name=FUNC_NAME, signature="10, 'abc'"
        ),
        mock_logger.logged_messages,
    )
    with pytest.raises(KeyError):
        DEBUG_END_FUNCTION_WORK_MSG.substitute(
            func_name=FUNC_NAME, signature="10, 'abc'"
        )
    assert check_msg_from_list_contains_text(
        DEBUG_END_FUNCTION_WORK_MSG.safe_substitute(
            func_name=FUNC_NAME, signature="10, 'abc'"
        ).split("work_time")[0],
        mock_logger.logged_messages,
    )


def test_sync_function_logs_exception(mock_logger: MockLogger):
    decorated = log(mock_logger)(sync_func_logging_testing)
    with pytest.raises(TypeError):
        decorated(10, "", None)  # type: ignore
    assert check_msg_from_list_contains_text(
        EXCEPTION_MSG.safe_substitute(func_name=FUNC_NAME).split("Description")[0],
        mock_logger.logged_messages,
    )
    assert check_msg_from_list_contains_text("TypeError", mock_logger.logged_messages)
