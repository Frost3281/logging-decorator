# **logging-decorator**

Декоратор для логирования с прокаченной типизацией.
<br><br><br>
Работает с асинхронными/синхронными функциями,
логирует в дебаге начало/завершение выполнения функции с переданными аргументами и временем работы функции. Логирует исключения.
Сохраняет исходную типизацию.

Применение:

```python
import logging
from dataclasses import dataclass

from logging_decorator import log

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(name)s - %(message)s')


@dataclass
class Example:

    a: int
    b: str


@log(logger)
def check_function(check_list: list[Example], dict_example: dict[str, str], param_w_default: int = 1) -> None:
    ...


def main() -> None:
    check_function([Example(1, '2'), Example(4, '5')], dict_example={'a': 'b'})


if __name__ == "__main__":
    main()
```

```
root - Функция "check_function" начала работу с аргументами:
  check_list: list = list(Example({'a': '...', 'b': '...'}), Example({'a': '...', 'b': '...'}))
  dict_example: dict = dict(a: 'b')
  param_w_default: int = 1.
root - Функция "check_function" завершила работу за 0.0003 сек.
```

По умолчанию глубина прохождения по аргументам = 1. Можно изменить с помощью **LogConfig**:

```python
from logging_decorator import LogConfig

@log(logger, LogConfig(max_depth=2))
def check_function(check_list: list[Example], dict_example: dict[str, str], param_w_default: int = 1) -> None:
    ...
```

```
root - Функция "check_function" начала работу с аргументами:
  check_list: list = list(Example({'a': '1', 'b': "'2'"}), Example({'a': '4', 'b': "'5'"}))
  dict_example: dict = dict(a: 'b')
  param_w_default: int = 1.
root - Функция "check_function" завершила работу за 0.0003 сек.
```

Аналогично работает с асинхронными функциями:

```python
import asyncio

@log(logger, LogConfig(max_depth=2))
async def check_function(check_list: list[Example], dict_example: dict[str, str], param_w_default: int = 1) -> None:
    ...


def main() -> None:
    asyncio.run(check_function([Example(1, '2'), Example(4, '5')], dict_example={'a': 'b'}))
```

Декоратору можно передавать также instance других logging-библиотек,
кроме стандартной библиотеки **logging**, например, **loguru**,
либо свои кастомные логгеры, соответствующие протоколу **Logger**.

```python
import loguru
from logging_decorator.logging_decorator import log


@log(logger=loguru.logger)
def check_function(check_list: list[str]) -> None:
    print(check_list)
```
