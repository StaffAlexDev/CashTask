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


def order_menu_kb(role):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="New order", callback_data="new_order"))
    builder.add(InlineKeyboardButton(text="Open orders", callback_data="open_orders"))
    if role == 'superadmin':
        builder.add(InlineKeyboardButton(text="Completed orders", callback_data="completed_orders"))
    builder.adjust(2)
    return builder.as_markup()


def clients_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Add client", callback_data="add_client"))
    builder.add(InlineKeyboardButton(text="Add car", callback_data="add_car"))
    builder.add(InlineKeyboardButton(text="Clients", callback_data="all_clients"))
    builder.add(InlineKeyboardButton(text="Cars", callback_data="all_cars"))
    builder.adjust(2)
    return builder.as_markup()
