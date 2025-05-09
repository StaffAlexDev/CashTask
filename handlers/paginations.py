from aiogram import F
from aiogram.types import CallbackQuery

from config.buttons_config import pagination_configs
from database.clients_pg import delete_client_by_id, get_car_by_id, get_client_by_id
from database.employees_pg import delete_car_by_id

from handlers.admins import admins
from keyboards.general.paginations import get_paginated_list


@admins.callback_query(F.data.startswith("item_"))
async def handle_item_action(callback: CallbackQuery):
    _, item_type, item_id, action = callback.data.split("_")
    item_id = int(item_id)
    user_id = callback.from_user.id
    if action == "edit":

        if item_type == "client":
            client = await get_client_by_id(item_id)
            msg = f"Редактирование клиента:\n{client['first_name']} {client['last_name']}"
        elif item_type == "car":
            car = await get_car_by_id(item_id)
            msg = f"Редактирование авто:\n{car['car_brand']} {car['car_model']}"
        else:
            msg = "Редактирование пока не реализовано."

        await callback.message.edit_text(msg)
        await callback.answer()

    elif action == "delete":

        if item_type == "client":
            success = delete_client_by_id(item_id, user_id)
            msg = "Клиент удалён." if success else "Ошибка при удалении клиента."

        elif item_type == "car":
            success = delete_car_by_id(item_id, user_id)
            msg = "Автомобиль удалён." if success else "Ошибка при удалении автомобиля."

        else:
            msg = "Удаление для этого типа пока не реализовано."

        await callback.message.edit_text(f"✅ {msg}")
        await callback.answer()


@admins.callback_query(F.data.startswith("back_to_list_"))
async def handle_back_to_list(callback: CallbackQuery):
    _, _, item_type, page = callback.data.split("_")
    page = int(page)

    config = pagination_configs.get(item_type)
    if not config:
        await callback.answer("Тип списка не распознан.", show_alert=True)
        return

    message, keyboard = get_paginated_list(
        get_items_func=config["get_items_func"],
        build_button_text=config["build_button_text"],
        callback_prefix=item_type,
        back_callback=config["back_callback"],
        title=config["title"],
        page=page
    )
    await callback.message.edit_text(message, reply_markup=keyboard)
    await callback.answer()


@admins.callback_query(F.data.startswith("prev_"))
async def prev_page(callback: CallbackQuery):
    _, page, prefix = callback.data.split("_")
    config = pagination_configs.get(prefix)
    if not config:
        await callback.answer("Неизвестный тип данных", show_alert=True)
        return

    page = int(page) - 1
    message, keyboard = get_paginated_list(
        get_items_func=config["get_items_func"],
        build_button_text=config["build_button_text"],
        callback_prefix=prefix,
        back_callback=config["back_callback"],
        title=config["title"],
        page=page
    )
    await callback.message.edit_text(message, reply_markup=keyboard)
    await callback.answer()


@admins.callback_query(F.data.startswith("next_"))
async def next_page(callback: CallbackQuery):
    _, page, prefix = callback.data.split("_")
    config = pagination_configs.get(prefix)
    if not config:
        await callback.answer("Неизвестный тип данных", show_alert=True)
        return

    page = int(page) + 1
    message, keyboard = get_paginated_list(
        get_items_func=config["get_items_func"],
        build_button_text=config["build_button_text"],
        callback_prefix=prefix,
        back_callback=config["back_callback"],
        title=config["title"],
        page=page
    )
    await callback.message.edit_text(message, reply_markup=keyboard)
    await callback.answer()
