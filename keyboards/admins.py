from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from database.db_crud import get_workers


def get_type_finance_kb(role):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Приход", callback_data="finance_income"))
    builder.add(InlineKeyboardButton(text="Расход", callback_data="finance_expense"))
    builder.add(InlineKeyboardButton(text="Топливо", callback_data="finance_fuel"))

    if role == "supervisor":
        builder.add(InlineKeyboardButton(text="Отчеты", callback_data="finance_report"))
    return builder.as_markup()


def get_finance_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="По машине", callback_data="from_car"))
    builder.add(InlineKeyboardButton(text="Инвестиция", callback_data="general"))
    return builder.as_markup()


def order_type_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Client", callback_data="by_client"))
    builder.add(InlineKeyboardButton(text="Car", callback_data="by_car"))
    builder.adjust(1)  # Одна кнопка в строке
    return builder.as_markup()


def get_cars_kb(cars):
    builder = InlineKeyboardBuilder()
    for car in cars:
        builder.add(
            InlineKeyboardButton(text=f"{car['car_brand']} {car['car_model']}", callback_data=f"car_{car['car_id']}"))
    builder.add(InlineKeyboardButton(text="Отменить", callback_data="cancel"))
    builder.adjust(1)  # Одна кнопка в строке
    return builder.as_markup()


def get_employer_kb():
    builder = InlineKeyboardBuilder()
    employees = get_workers()
    for employer in employees:
        builder.add(
            InlineKeyboardButton(text=f"{employer['first_name']}", callback_data=f"employer_{employer['user_id']}"))
    builder.add(InlineKeyboardButton(text="Отменить", callback_data="cancel"))
    builder.adjust(2)  # Одна кнопка в строке
    return builder.as_markup()


def get_confirmation_kb():
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="Подтвердить", callback_data="confirm")
    )
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="back"),
        InlineKeyboardButton(text="Отменить", callback_data="cancel")
    )

    return builder.as_markup()
