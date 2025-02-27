from string import Template

DEBUG_START_FUNCTION_WORK_MSG = Template("Функция '$func_name' начала работу$signature.")
DEBUG_END_FUNCTION_WORK_MSG = Template(
    "Функция '$func_name' завершила работу. Время работы: $work_time сек.$signature",
)
EXCEPTION_MSG = Template("Возникла ошибка при работе функции '$func_name'$signature.")
