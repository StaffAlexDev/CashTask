from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import BUTTONS_FOR_ROLE, BUTTONS, USER_ROLES


def roles_kb() -> InlineKeyboardMarkup:
    roles = USER_ROLES[:-1]
    print(roles)
    builder = InlineKeyboardBuilder()
    print("Создание клавиатуры для роли")
    for role in roles:
        builder.button(text=role, callback_data=f"role_{role}")

        print(f"callback_data: {role}")
    builder.adjust(2)  # Распределяем кнопки по 2 в ряд
    return builder.as_markup()


def get_access_confirmation(new_worker) -> InlineKeyboardMarkup:
    button1 = InlineKeyboardButton(text="Accept", callback_data=f"access_accept_{new_worker}")
    button2 = InlineKeyboardButton(text="Reject", callback_data=f"access_reject_{new_worker}")

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


def clients_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="Add client", callback_data="add_client"))
    builder.add(InlineKeyboardButton(text="Add car", callback_data="add_car"))
    builder.add(InlineKeyboardButton(text="Clients", callback_data="all_clients"))
    builder.add(InlineKeyboardButton(text="Cars", callback_data="all_cars"))

    builder.adjust(2)
    return builder.as_markup()


def get_car_keyboard_from_list(cars: list[tuple]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for car in cars:
        car_id, first_name, last_name, phone, model, year, plate = car
        button_text = f"{first_name} {last_name} • {model} ({year}) • {plate}"
        if len(button_text) > 64:
            button_text = button_text[:61] + "..."

        builder.add(InlineKeyboardButton(
            text=button_text,
            callback_data=f"car_id_{car_id}"
        ))

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
