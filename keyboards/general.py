from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import BUTTONS_FOR_ROLE, BUTTONS, USER_ROLES


def roles_kb():
    roles = USER_ROLES[:-1]
    print(roles)
    builder = InlineKeyboardBuilder()
    for role in roles:
        builder.button(text=role, callback_data=f"role_{role}")
    builder.adjust(2)  # Распределяем кнопки по 2 в ряд
    return builder.as_markup()


def get_access_confirmation():
    button1 = InlineKeyboardButton(text="Accept", callback_data="accept")
    button2 = InlineKeyboardButton(text="Reject", callback_data="reject")

    confirm_kb = InlineKeyboardMarkup(inline_keyboard=[[button1, button2]])
    return confirm_kb


def menu_by_role(role):

    builder = InlineKeyboardBuilder()
    role_btn = BUTTONS_FOR_ROLE[role]
    for btn in role_btn:
        builder.button(text=BUTTONS[btn].get("text"), callback_data=BUTTONS[btn].get("callback_data"))
    builder.adjust(2)
    return builder.as_markup()


