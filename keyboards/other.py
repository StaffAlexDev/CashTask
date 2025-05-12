from enum import Enum
from typing import Iterable, Union, List, Tuple

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config.buttons_config import BUTTONS_COMMON
from languages.lang_base import LangBase
from utils.enums import Role


def enum_kb(
    items: Iterable[Union[Enum, str]],
    lang_data: dict,
    callback_prefix: str,
    per_row: int = 2
) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    for item in items:
        if isinstance(item, Enum):
            callback_value = str(item.value).strip()
            text = item.display_name(lang_data) if hasattr(item, "display_name") else callback_value

        else:
            callback_value = str(item).strip()
            text = callback_value

        # Проверяем чтобы callback был валиден
        if not callback_value or " " in callback_value or "." in callback_value:
            raise ValueError(f"Invalid callback_data value: {callback_value}")

        builder.button(text=text, callback_data=f"{callback_prefix}_{callback_value}")
        print(f"btn: text-{text}\n callback: {callback_prefix}_{callback_value}")
    builder.adjust(per_row)
    return builder.as_markup()


def get_ui_button(name: str, lang_data: dict) -> InlineKeyboardButton:
    text = lang_data.get("ui_buttons", {}).get(name, name)  # Fallback на name если перевода нет
    return InlineKeyboardButton(text=text, callback_data=name)


def ui_buttons_kb(button_names: list[str], lang_data: dict, per_row: int = 2) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for name in button_names:
        builder.add(get_ui_button(name, lang_data))

    builder.adjust(per_row)
    return builder.as_markup()


# def ui_buttons_for_role(role: Role, lang_data: dict) -> InlineKeyboardMarkup:
#     button_keys = BUTTONS_FOR_ROLE.get(role.value, [])
#     return ui_buttons_kb(button_keys, lang_data)


def get_access_confirmation(key: str, lang_data: LangBase) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения доступа"""
    print("Кнопки подтверждения в get_access_confirmation")
    print(lang_data.ui_buttons.access_accept, f"access_accept_{key}")
    print(lang_data.ui_buttons.access_reject, f"access_reject_{key}")
    return common_kb_by_role(
        "control",
        lang_data,
        Role.SUPERADMIN,  # Максимальные права для подтверждения
        per_row=2,
        custom_buttons=[
            (lang_data.ui_buttons.access_accept, f"access_accept_{key}"),
            (lang_data.ui_buttons.access_reject, f"access_reject_{key}")
        ]
    )


def car_employer_menu_kb(car_id, lang_data):
    buttons = [
        (lang_data.ui_buttons.edit, f"car_employer_{car_id}_edit"),
        (lang_data.ui_buttons.delete, f"car_employer_{car_id}_delete")
    ]
    return inline_pairs_kb(buttons)


def inline_pairs_kb(pairs: List[Tuple[str, str]], per_row: int = 2) -> InlineKeyboardMarkup:
    """Универсальная клавиатура для пар (текст, callback)"""
    builder = InlineKeyboardBuilder()
    for text, callback in pairs:
        builder.button(text=text, callback_data=callback)
    builder.adjust(per_row)
    return builder.as_markup()


def common_kb_by_role(
        category: str,
        lang_data: LangBase,
        role: Role,
        per_row: int = 2,
        custom_buttons: list[tuple[str, str]] | None = None,
        **kwargs
        ) -> InlineKeyboardMarkup:
    if custom_buttons:
        return inline_pairs_kb(custom_buttons, per_row=per_row)

    raw = BUTTONS_COMMON.get(category, [])
    """
    Универсальный генератор клавиатур по категориям и ролям

    :param category: ключ из BUTTONS_COMMON
    :param lang_data: языковые данные (user.lang)
    :param role: роль пользователя
    :param per_row: количество кнопок в ряду
    :param kwargs: дополнительные параметры для форматирования текста
    """
    raw = BUTTONS_COMMON.get(category, [])

    # Получаем все ключи кнопок для данной роли
    if isinstance(raw, dict):
        keys = list(raw.get("base", []))
        keys += raw.get(role.value, [])
        keys = list(dict.fromkeys(keys))  # Удаляем дубли с сохранением порядка
    else:
        keys = raw

    # Формируем пары (текст, callback_data)
    buttons = []
    for key in keys:
        # Получаем локализованный текст
        text = getattr(lang_data.ui_buttons, key, key)
        # Форматируем текст если нужно
        if kwargs:
            text = text.format(**kwargs)
        buttons.append((text, key))

    return inline_pairs_kb(buttons, per_row=per_row)
