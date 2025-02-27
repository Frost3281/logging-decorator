import inspect
from typing import Any

from logging_decorator.config import LogConfig


def pretty_repr(obj: Any, config: LogConfig, depth: int = 0) -> str:
    """Рекурсивное форматирование объектов с ограничением глубины."""
    if depth > 1:  # ограничение глубины вложенности
        return "..."

    if isinstance(obj, (int, float, bool, type(None))):
        return repr(obj)

    if isinstance(obj, str):
        if config.max_arg_length and len(obj) > config.max_arg_length:
            return f"'{obj[:config.max_arg_length - 3]}...'"
        return f"'{obj}'"

    if isinstance(obj, (list, tuple, set)):
        items = [pretty_repr(x, config, depth + 1) for x in obj]
        if config.max_arg_length and len(items) > 5:
            items = items[:5] + ["..."]
        return f"{type(obj).__name__}({', '.join(items)})"

    if isinstance(obj, dict):
        items = [
            f"{k}: {pretty_repr(v, config, depth + 1)}"
            for k, v in list(obj.items())[:5]
        ]
        if config.max_arg_length and len(obj) > 5:
            items.append("...")
        return f"dict({', '.join(items)})"

    try:
        attrs = {
            k: pretty_repr(v, config, depth + 1)
            for k, v in inspect.getmembers(obj)
            if not k.startswith("_") and not inspect.ismethod(v)
        }
        return f"{obj.__class__.__name__}({attrs})"
    except Exception:
        return f"{obj.__class__.__name__} instance"
