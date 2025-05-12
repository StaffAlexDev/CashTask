import re

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config.buttons_config import pagination_configs
from config.patterns import SOCIAL_PATTERN
from database.clients_pg import add_client, add_car, get_client_id_by_name
from database.state_models import ClientStates
from handlers.admins import admins
from keyboards.paginations import get_paginated_list
from utils import validate_car_data
from utils.validators import validate_contact, is_phone_number, normalize_number


@admins.callback_query(F.data.startswith("add_"))
async def handle_add_item(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    action = callback.data.split("_")[1]
    match action:
        case "client":
            await callback.message.edit_text("Введите данные о клиенте одним сообщением через запятую ','\n"
                                             "Имя Фамилия, телефона, соцсеть "
                                             "(или что то одно: телефон или соцсеть)")
            await state.set_state(ClientStates.new_client_data)

        case "car":
            await callback.message.edit_text("Введите данные об автомобиле одним сообщением через запятую ','\n"
                                             "Имя клиента, марка, модель, гос. номер, VIN")
            await state.set_state(ClientStates.new_car_data)


@admins.message(ClientStates.new_client_data)
async def new_client_info(message: Message, state: FSMContext):
    await state.clear()
    text = message.text.strip()

    validation = validate_contact(text)
    if validation["status"] != "ok":
        await message.answer(f"❌ Ошибка в данных: {validation['error']}")
        return

    parts = [part.strip() for part in text.split(",", maxsplit=2)]
    name_part = parts[0]
    contacts = parts[1:]

    name_parts = name_part.split(maxsplit=1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    phone, social = None, None
    for contact in contacts:
        if is_phone_number(contact):
            phone = normalize_number(contact)
        elif re.match(SOCIAL_PATTERN, contact, re.IGNORECASE):
            social = contact.lower()

    if not (phone or social):
        await message.answer("❌ Необходимо указать хотя бы один контакт (телефон или соцсеть)")
        return

    try:
        await add_client(
            first_name=first_name,
            last_name=last_name if last_name else None,
            phone_number=phone,
            social_network=social
        )
        await message.answer("✅ Клиент успешно добавлен!")
    except Exception as e:
        await message.answer(f"❌ Ошибка при добавлении клиента: {str(e)}")


@admins.message(ClientStates.new_car_data)
async def client_car_info(message: Message, state: FSMContext):
    await state.clear()

    try:
        parts = [part.strip() for part in message.text.split(",")]

        if len(parts) < 4:
            await message.answer("❌ Недостаточно данных. Формат: <code>Имя клиента, Марка, Модель, Номер[, VIN]</code>")
            return

        client_name = parts[0]
        clients_list = await get_client_id_by_name(client_name)

        if not clients_list:
            await message.answer(f"❌ Клиент '{client_name}' не найден")
            return

        if len(clients_list) > 1:
            await message.answer(f"❌ Найдено несколько клиентов с именем '{client_name}'. Уточните имя.")
            return

        client_id = clients_list[0]["client_id"]

        car_info = {
            "brand": parts[1],
            "model": parts[2],
            "license_plate": parts[3],
            "vin_code": parts[4] if len(parts) > 4 else None
        }

        validation = validate_car_data("client", car_info)
        if validation["status"] != "ok":
            errors = "\n".join([f"• {e['error']}" for e in validation["errors"]])
            await message.answer(f"❌ Ошибки в данных:\n{errors}")
            return

        success, msg = add_car(
            client_id=client_id,
            car_brand=car_info["brand"],
            car_model=car_info["model"],
            license_plate=car_info["license_plate"],
            vin_code=car_info.get("vin_code")
        )

        if success:
            await message.answer("✅ Автомобиль успешно добавлен")
        else:
            await message.answer(f"❌ {msg}")

    except Exception as e:
        await message.answer(f"❌ Произошла ошибка: {str(e)}")


@admins.callback_query(F.data.startswith("all_"))
async def handle_all_items(callback: CallbackQuery):
    await callback.answer()

    prefix = callback.data.split("_")[1]
    config = pagination_configs.get(prefix)
    if not config:
        await callback.answer("Неизвестный тип данных", show_alert=True)
        return

    page = 1

    filters = config.get("filters") or {}

    message, keyboard = get_paginated_list(
        get_items_func=config["get_items_func"],
        build_button_text=config["build_button_text"],
        callback_prefix=prefix,
        back_callback=config["back_callback"],
        title=config["title"],
        page=page,
        **filters
    )

    await callback.message.edit_text(message, reply_markup=keyboard)
