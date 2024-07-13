def to_camel_case(snake: str) -> str:
    if not snake:
        return ""

    words: list[str] = snake.split("_")
    return words[0] + "".join(word.capitalize() for word in words[1:])
