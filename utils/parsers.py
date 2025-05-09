from typing import Type, Optional, TypeVar, Tuple
from enum import Enum

from config.patterns import INVOICE_PATTERN
from utils.validators import normalize_payment_type

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


def parse_invoice(text: str) -> Tuple[bool, Optional[dict], str]:
    """
    Парсит строку инвойса.
    Возвращает кортеж (успех, данные, сообщение об ошибке)
    """

    match = INVOICE_PATTERN.match(text)
    if not match:
        return False, None, "❗ Неверный формат. Пример: +500 нал покупка материалов"

    amount_raw = match.group("amount")
    payment_type_raw = match.group("payment_type")
    description = match.group("description").strip()

    # Проверка суммы
    try:
        amount = int(amount_raw)
    except ValueError:
        return False, None, "❗ Сумма указана неверно. Пример: +500 или -200"

    # Проверка типа оплаты
    payment_type = normalize_payment_type(payment_type_raw)
    if not payment_type:
        return False, None, "❗ Тип оплаты указан неверно. Используйте 'нал' или 'безнал'."

    # Проверка описания
    if not description or description.isspace():
        return False, None, "❗ Описание не может быть пустым."

    return True, {
        "amount": amount,
        "payment_type": payment_type,
        "description": description
    }, ""
