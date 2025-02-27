import inspect
from functools import singledispatch
from typing import Any, Union

from logging_decorator.config import LogConfig


@singledispatch
def pretty_repr(obj: Any, config: LogConfig, depth: int = 0) -> str:  # noqa: ANN401
    """Рекурсивное форматирование объектов."""
    def _get_repr_with_getmembers() -> str:
        attrs = {
            k: pretty_repr(v, config, depth + 1)
            for k, v in inspect.getmembers(obj)
            if not k.startswith('_') and not inspect.ismethod(v)
        }
        return f'{obj.__class__.__name__}({attrs})'

    def _get_repr_with_dict() -> str:
        try:
            attrs = {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        except Exception:  # noqa: BLE001
            return f'{obj.__class__.__name__} instance'
        else:
            return f'{obj.__class__.__name__}({attrs})'

    if depth > 1:
        return '...'
    try:
        return _get_repr_with_getmembers()
    except Exception:  # noqa: BLE001
        return _get_repr_with_dict()


@pretty_repr.register(int)
@pretty_repr.register(float)
@pretty_repr.register(bool)
@pretty_repr.register(type(None))
def _(obj: Union[float, bool, None], config: LogConfig, depth: int = 0) -> str:  # noqa: FBT001, ARG001
    if depth > 1:
        return '...'
    return repr(obj)


@pretty_repr.register(str)
def _(obj: str, config: LogConfig, depth: int = 0) -> str:
    if depth > 1:
        return '...'
    if config.max_arg_length and len(obj) > config.max_arg_length:
        return f"'{obj[: config.max_arg_length - 3]}...'"
    return f"'{obj}'"


@pretty_repr.register(list)
@pretty_repr.register(tuple)
@pretty_repr.register(set)
def _(obj: Union[list, tuple, set], config: LogConfig, depth: int = 0) -> str:
    items = [pretty_repr(x, config, depth + 1) for x in obj]
    if config.max_arg_length and len(items) > 5:
        items = items[:5] + ['...']
    return f'{type(obj).__name__}({", ".join(items)})'


@pretty_repr.register(dict)
def _(obj: dict, config: LogConfig, depth: int = 0) -> str:
    items = [
        f'{k}: {pretty_repr(v, config, depth + 1)}' for k, v in list(obj.items())[:5]
    ]
    if config.max_arg_length and len(obj) > 5:
        items.append('...')
    return f'dict({", ".join(items)})'
