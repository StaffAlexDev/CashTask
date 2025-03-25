from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import USER_ROLES


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
    buttons = {
        "car_in_work": {"text": "Авто в работе", "callback_data": "car_in_work"},
        "accept": {"text": "Нужны материалы", "callback_data": "accept"},
        "add_car": {"text": "Добавить авто", "callback_data": "add_car"},
        "add_task": {"text": "Добавить задачу", "callback_data": "add_task"},
        "what_buy": {"text": "Что купить", "callback_data": "what_buy"},
        "reports": {"text": "Отчеты", "callback_data": "reports"}
    }
    btn_for_role = {
        "worker": ["car_in_work", "accept"],
        "admin": ["car_in_work", "accept", "add_car", "add_task", "what_buy", "income_expense"],
        "super_admin": ["car_in_work", "what_buy", "income_expense", "reports"],
    }
    builder = InlineKeyboardBuilder()
    role_btn = btn_for_role[role]
    for btn in role_btn:
        builder.button(text=buttons[btn].get("text"), callback_data=buttons[btn].get("callback_data"))
    builder.adjust(2)
    return builder.as_markup()


