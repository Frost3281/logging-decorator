def check_msg_from_list_contains_text(
    contains_text: str,
    messages: list[str],
) -> bool:
    return any(
        contains_text in msg for msg in messages if not isinstance(msg, (int, float))
    )
