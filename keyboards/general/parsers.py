from typing import Type, Optional, TypeVar
from enum import Enum

T = TypeVar("T", bound=Enum)


def parse_enum_callback(callback_data: str, callback_prefix: str, enum_cls: Type[T]) -> Optional[T]:
    """
    Парсит callback_data и возвращает Enum, если возможно.

    :param callback_data: строка вида "prefix_value"
    :param callback_prefix: префикс (например "role", "order_status")
    :param enum_cls: класс Enum
    :return: Enum или None, если не найдено/невалидно
    """

    parts = callback_data.split("_", 1)

    if len(parts) != 2:
        return None

    prefix, value = parts

    if prefix != callback_prefix:
        return None

    try:
        return enum_cls(value)
    except ValueError:
        return None
