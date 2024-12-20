from string import Template

DEBUG_START_FUNCTION_WORK_MSG = Template(
    "Функция '$func_name' начала работу.",
)
DEBUG_END_FUNCTION_WORK_MSG = Template(
    "Функция '$func_name' завершила работу. Время работы функции: $work_time сек.",
)
EXCEPTION_MSG = Template(
    "Возникла ошибка при работе функции '$func_name'.",
)
