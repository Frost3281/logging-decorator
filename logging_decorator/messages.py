from string import Template


DEBUG_START_FUNCTION_WORK_MSG = Template(
    "function '$func_name' called with args $signature",
)
DEBUG_END_FUNCTION_WORK_MSG = Template(
    "function '$func_name' ended job with args $signature, work_time = $work_time",
)
EXCEPTION_MSG = Template(
    "Exception raised in '$func_name'. Description: $exc_repr. "
    + "Function args: $signature",
)
