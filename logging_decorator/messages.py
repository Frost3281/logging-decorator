from string import Template


DEBUG_START_FUNCTION_WORK_MSG = Template(
    "Функция '$func_name' начала работу с аргументами $signature",
)
DEBUG_END_FUNCTION_WORK_MSG = Template(
    "Функция '$func_name' завершила работу за $work_time сек. "
    + "В неё были переданы следующие аргументы: $signature",
)
EXCEPTION_MSG = Template(
    "Возникла ошибка при работе функции '$func_name'. Описание: $exc_repr. "
    + "Аргументы, передаваемые в функцию: $signature",
)
