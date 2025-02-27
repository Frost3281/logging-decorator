from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class LogConfig:
    """Конфигурация логирования."""

    include_args: bool = True
    max_arg_length: Union[int, None] = 100
    show_types: bool = True
