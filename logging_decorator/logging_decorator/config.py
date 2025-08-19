from dataclasses import dataclass, field
from typing import Iterable, Union


@dataclass(frozen=True)
class LogConfig:
    """Конфигурация логирования."""

    include_args: bool = True
    max_arg_length: Union[int, None] = 100
    show_types: bool = True
    skipped_args: Iterable[str] = field(default_factory=list)
    max_depth: int = 1
    show_complex_args: bool = False

    @classmethod
    def from_config(
        cls,
        config: 'LogConfig',
        **kwargs: bool | int | None | str,
    ) -> 'LogConfig':
        """Создание конфигурации логирования."""
        return cls(**{**config.__dict__, **kwargs})
