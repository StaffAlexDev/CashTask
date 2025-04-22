
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.db_crud import (add_employee_approval, add_employee, get_approver_employees_telegram_id, get_employer_car,
                              add_employer_car, delete_car_by_id, edit_car_info, get_role_by_telegram_id)
from database.state_models import UserCookies, EmployerCarParkMenu
from keyboards.general import get_access_confirmation, menu_by_role, car_employer_menu_kb
from settings import bot
from utils import is_text_patterns, is_likely_license_plate, is_data

general = Router()


@general.callback_query(F.data.startswith('role_'))
async def choice_role(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    print(f"tg: {callback_query.from_user.id}")
    print(f"name: {callback_query.from_user.first_name}")
    print(f"role: {callback_query.data.split("_")[1]}")
    user_id = callback_query.message.from_user.id
    lang = UserCookies(user_id).get_lang()
    lng_message = lang.get("info").get("user_accept")
    msg_list = lng_message.split(":")
    message = msg_list[0] + callback_query.from_user.first_name + msg_list[1]
    user_role = callback_query.data.split("_")[1]
    print(f"user_role: {user_role}")
    await state.update_data(user_role=user_role)
    new_worker = {
        "telegram_id": callback_query.from_user.id,
        "first_name": callback_query.from_user.first_name,
        "last_name": callback_query.from_user.last_name,
    }
    print(new_worker)
    await state.update_data(new_worker=new_worker)
    # Уходит запрос на должность выше
    role_list = get_approver_employees_telegram_id(user_role)
    print(f"role_list_id {role_list}")
    print(f"role_list_id {role_list[0]}")
    print(f"len role list: {len(role_list)}")
    for telegram_id in role_list:
        await bot.send_message(chat_id=telegram_id,
                               text=message,
                               reply_markup=get_access_confirmation())

    lng_msg = lang.get('unknown_user').get('waiting_accept')
    msg_list = lng_msg.split(":")
    sec_message = f"{msg_list[0]} {callback_query.data.split("_")[1]}{msg_list[1]}"
    print(f"msg_list {msg_list}")
    print(f"lng_msg {lng_msg}")
    print(f"callback_query {callback_query.from_user.first_name}")
    await callback_query.message.answer(sec_message)


# TODO Исправить передачу данных не через state, а напрямую через callback_data и создаваемой клавиатуре
@general.callback_query(F.data == 'accept')
async def get_accept_by_new_user(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    new_user = data.get("new_worker")
    user_role = data.get("user_role")
    if not new_user:
        await callback_query.answer("Ошибка: нет данных о пользователе.")
        print(f"new_user object: {new_user}")
        return

    # Добавляем пользователя в БД
    senior_telegram_id = callback_query.from_user.id

    add_employee(new_user.get("telegram_id"),
                 new_user.get("first_name"),
                 user_role)
    add_employee_approval(senior_telegram_id, new_user.get("telegram_id"))

    await callback_query.answer("Пользователь успешно подтверждён!")
    await bot.send_message(chat_id=new_user.get("telegram_id"),
                           text="Ваша заявка принята",
                           reply_markup=menu_by_role(user_role))
    await state.clear()


@general.callback_query(F.data == 'reject')
async def get_reject_by_new_user(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    new_user = data.get("new_user")
    await callback_query.answer("Пользователь отклонён!")
    await bot.send_message(chat_id=new_user.get("telegram_id"),
                           text="Ваша заявка отклонена")
    await state.clear()


@general.callback_query(F.data.startswith('lang_'))
async def get_selected_language(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user = UserCookies(user_id)
    selected_language = F.data.split("_")[1]
    user.update_profile(lang=selected_language)
    lang = user.get_lang()
    await callback_query.answer(lang.get("language").get("accept_lang"))


# Автопарк сотрудников
@general.callback_query(F.data.startswith('my_park_'))
async def my_park_actions(callback_query: CallbackQuery, state: FSMContext):
    action = callback_query.data.split("_")[2]
    employer_id = callback_query.from_user.id
    await callback_query.answer()
    match action:
        case "list":
            car_list = get_employer_car(employer_id)
            text = ''
            for car in car_list:
                car_id = car.get("car_id")
                car_data = f"""{car.get("car_brand")}, {car.get("car_model")}\n
                                {car.get("license_plate")},\n
                                {car.get("technical_inspection")},\n
                                {car.get("insurance")}"""
                text.join(car_data + "\n\n")
                await callback_query.message.answer(text, reply_markup=car_employer_menu_kb(car_id))

        case "add":
            text = (f"Запиши через запятую данные машины:\n"
                    f"(марка, модель, номерной знак, дата окончания тех. осмотра(день.месяц.год), "
                    f"дата окончания страховки(день.месяц.год)):\n")
            await callback_query.message.answer(text)
            await state.set_state(EmployerCarParkMenu.waiting_for_new_car)


@general.message(EmployerCarParkMenu.waiting_for_new_car)
async def employer_car_info(message: Message, state: FSMContext):
    await state.clear()
    data = [x.strip() for x in message.text.split(",")]
    is_text_status = is_text_patterns(data).get("status")

    if is_text_status == "ok":
        brand, model, plate, tech_date, ins_date = data
        employer_id = message.from_user.id
        result = add_employer_car(employer_id, brand, model, plate, tech_date, ins_date)
        status = result.get("status")
        await message.answer(status)

    else:
        await message.answer(f"Error: {is_text_status}")
        text = (f"Запиши через запятую данные машины:\n"
                f"(марка, модель, номерной знак, дата окончания тех. осмотра(день.месяц.год), "
                f"дата окончания страховки(день.месяц.год)):\n")
        await message.answer(text)
        await state.set_state(EmployerCarParkMenu.waiting_for_new_car)


# Действия для всех машин работника
@general.callback_query(F.data.startswith('car_employer_'))
async def my_park_actions(callback_query: CallbackQuery):
    action = callback_query.data.split("_")[-1]
    employer_id = callback_query.from_user.id
    await callback_query.answer()
    match action:
        case "edit":
            pass
        case "delete":
            car_id = callback_query.data.split("_")[2]
            result = delete_car_by_id(employer_id, car_id)
            if result:
                await callback_query.message.answer("Авто было удалено!")
            else:
                await callback_query.message.answer("Возникла проблема обратитесь в support!")


# Действия с конкретной машиной работника
@general.callback_query(F.data.startswith('car_employer_'))
async def my_park_actions(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    actions = {"plate": "Номерного знака", "inspection": "Техосмотра", "insurance": "Страховки"}
    action = callback_query.data.split("_")[-1]
    car_id = callback_query.data.split("_")[2]
    car = {"action": action, "car_id": car_id}
    await state.update_data(car=car)
    await callback_query.message.answer(f"Введите новые данные для {actions[action]}")
    await state.set_state(EmployerCarParkMenu.waiting_for_new_data_for_car)


@general.message(EmployerCarParkMenu.waiting_for_new_car)
async def employer_car_info(message: Message, state: FSMContext):
    actions = {"plate": "license_plate", "inspection": "technical_inspection", "insurance": "insurance"}
    user_id = message.from_user.id
    role = get_role_by_telegram_id(user_id)
    data = await state.get_data()
    text = message.text
    car = data.get("car")
    car_id = car.get("car_id")
    action = car.get("action")
    # TODO не забыть протестировать всю цепочку
    if action == "plate":
        if is_likely_license_plate(text):
            result = edit_car_info(actions.get(action), text, car_id)
            if result > 0:
                await message.answer(f"Номерной знак изменен на {text}", reply_markup=menu_by_role(role))

            await message.answer(f"Это не похоже на известные мне виды номеров повторите ввод")
            await state.clear()
            await state.set_state(EmployerCarParkMenu.waiting_for_new_data_for_car)

    else:
        if is_data(text):
            result = edit_car_info(actions.get(action), text, car_id)
            if result > 0:
                await message.answer(f"Номерной знак изменен на {text}", reply_markup=menu_by_role(role))

            await message.answer("Вы ввели неподходящие значения даты, нужно так: Д.М.Г")
            await state.clear()
            await state.set_state(EmployerCarParkMenu.waiting_for_new_data_for_car)

    await state.clear()
