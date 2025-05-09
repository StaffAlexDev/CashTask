from enum import Enum
from typing import Iterable, Union

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config.buttons_config import BUTTONS_FOR_ROLE, BUTTONS
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


def ui_buttons_for_role(role: Role, lang_data: dict) -> InlineKeyboardMarkup:
    button_keys = BUTTONS_FOR_ROLE.get(role.value, [])
    return ui_buttons_kb(button_keys, lang_data)


def get_access_confirmation(key) -> InlineKeyboardMarkup:
    button1 = InlineKeyboardButton(text="Accept", callback_data=f"access_accept_{key}")
    button2 = InlineKeyboardButton(text="Reject", callback_data=f"access_reject_{key}")

    confirm_kb = InlineKeyboardMarkup(inline_keyboard=[[button1, button2]])
    return confirm_kb


def menu_by_role(role: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    role_btn = BUTTONS_FOR_ROLE[role]

    for btn in role_btn:
        builder.button(text=BUTTONS[btn].get("text"), callback_data=BUTTONS[btn].get("callback_data"))

    builder.adjust(2)
    return builder.as_markup()


def order_menu_kb(role: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="New order", callback_data="new_order"))
    builder.add(InlineKeyboardButton(text="Open orders", callback_data="open_orders"))

    if role == 'superadmin':
        builder.add(InlineKeyboardButton(text="Completed orders", callback_data="completed_orders"))

    builder.adjust(2)
    return builder.as_markup()


def car_park_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Car list", callback_data="my_park_list"))
    builder.add(InlineKeyboardButton(text="Add car", callback_data="my_park_add"))
    builder.adjust(2)
    return builder.as_markup()


def car_employer_menu_kb(car_id):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Delete", callback_data=f"car_employer_{car_id}_delete"))
    builder.add(InlineKeyboardButton(text="Edit", callback_data=f"car_employer_{car_id}_edit"))
    builder.adjust(2)
    return builder.as_markup()


def employer_car_menu_kb(car_id):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Номерной знак", callback_data=f"employer_car_{car_id}_plate"))
    builder.add(InlineKeyboardButton(text="Техосмотр", callback_data=f"employer_car_{car_id}_inspection"))
    builder.add(InlineKeyboardButton(text="Страховка", callback_data=f"employer_car_{car_id}_insurance"))
    builder.adjust(2)
    return builder.as_markup()


def get_cars_kb(cars):
    builder = InlineKeyboardBuilder()
    for car in cars:
        builder.add(
            InlineKeyboardButton(text=f"{car['car_brand']} {car['car_model']}",
                                 callback_data=f"car_{car['car_id']}"))
    builder.add(InlineKeyboardButton(text="Отменить", callback_data="cancel"))
    builder.adjust(2)
    return builder.as_markup()
