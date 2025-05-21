from enum import Enum
from typing import Iterable, Union, List, Tuple

from aiogram.types import InlineKeyboardMarkup
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


def get_access_confirmation(key: str, lang_data: LangBase) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения доступа"""

    return common_kb_by_role(
        "control",
        lang_data,
        Role.SUPERVISOR,  # Максимальные права для подтверждения
        per_row=2,
        custom_buttons=[
            (lang_data.ui_buttons.access_accept, f"access_accept_{key}"),
            (lang_data.ui_buttons.access_reject, f"access_reject_{key}")
        ]
    )


def get_navigate_kb(lang_data, views: int):
    """
    Клавиатура навигации для FSM-состояний.

    :param lang_data: словарь локализации (user.lang)
    :param views: строка "1"–"4", определяющая, сколько кнопок показать
    :return: InlineKeyboardMarkup
    """
    # Все возможные кнопки навигации, в порядке приоритета
    raw = BUTTONS_COMMON.get("navigation", [])

    # Для каждого уровня views — свой набор ключей
    btn_by_views = {
        "1": ["back"],
        "2": ["back", "cancel"],
        "3": ["back", "cancel", "main_menu"],
        "4": ["back", "main_menu", "cancel", "close"],
    }

    # Берём нужные ключи (или пустой список, если views некорректно)
    keys = btn_by_views.get(str(views), [])

    # Строим список пар (текст кнопки, callback_data)
    buttons = []
    for key in keys:
        if key in raw:  # на всякий случай проверяем, что ключ есть в raw
            text = getattr(lang_data.ui_buttons, key)
            buttons.append((text, key))
    print(buttons)
    # Собираем InlineKeyboardMarkup из этих пар
    return inline_pairs_kb(buttons)


def car_employer_menu_kb(car_id: int, lang_data: LangBase):
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

    buttons = []
    for key in keys:
        # Получаем локализованный текст
        text = getattr(lang_data.ui_buttons, key, key)
        if kwargs:
            text = text.format(**kwargs)
        buttons.append((text, key))

    return inline_pairs_kb(buttons, per_row=per_row)
