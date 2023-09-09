def check_msg_from_list_contains_text(
    contains_text: str,
    messages: list[str],
) -> bool:
    return any([msg.__contains__(contains_text) for msg in messages])
