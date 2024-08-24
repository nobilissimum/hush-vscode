from typing import Any


def to_camel_case(snake: str) -> str:
    if not snake:
        return ""

    words: list[str] = snake.split("_")
    return words[0] + "".join(word.capitalize() for word in words[1:])


def sort_dictionary(dictionary_obj: dict) -> dict:
    sorted_list: list = sorted(dictionary_obj.items())

    sorted_dict: dict = {}
    for key, value in sorted_list:
        if isinstance(value, list):
            sorted_dict[key] = sorted(value)
            continue

        if isinstance(value, dict):
            sorted_dict[key] = sort_object(value)
            continue

        sorted_dict[key] = value

    return sorted_dict


def sort_dictionary_list(dictionary: dict, key: str) -> str | int:
    value: Any = dictionary.get(key, "")
    if not isinstance(value, str):
        return ""

    return value


def sort_list(list_obj: list, key: str = "key") -> list:
    if not list_obj:
        return list_obj

    item: Any = list_obj[0]
    if isinstance(item, str):
        return sorted(list_obj)

    if isinstance(item, dict):
        return sorted(list_obj, key=lambda x: sort_dictionary_list(x, key))

    return list_obj


def sort_object(obj: dict | list) -> dict:
    if isinstance(obj, dict):
        return sort_dictionary(obj)

    if isinstance(obj, list):
        return sort_list(obj)

    return obj
