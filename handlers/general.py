
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.employees_pg import get_approver_employees_telegram_id, add_employee, add_employee_approval, \
    get_employer_car, add_employer_car, delete_employer_car_by_id, edit_car_info
from database.general_pg import add_temporary_data, get_temp_data
from database.state_models import UserContext, EmployerState
from keyboards.general.other import get_access_confirmation, menu_by_role, car_employer_menu_kb, ui_buttons_for_role
from utils.parsers import parse_enum_callback
from settings import bot
from utils import validate_car_data, is_likely_license_plate, is_date
from utils.enums import Role

general = Router()


@general.callback_query(F.data.startswith('role_'))
async def choice_role(callback: CallbackQuery, user: UserContext):
    await callback.answer()
    role = parse_enum_callback(callback.data, "role", Role)
    user_name = callback.from_user.first_name
    lang = user.lang
    message = lang.info.new_user_info_notif.format(name=user_name, position=role.value)
    print(f"message: {message}")
    telegram_id = callback.from_user.id
    first_name = callback.from_user.first_name

    new_worker_data = {
                       "telegram_id": telegram_id,
                       "first_name": first_name,
                       "role": role.value
                       }
    print(new_worker_data)
    key = await add_temporary_data(new_worker_data)
    print(f" key: {key}")
    # Уходит запрос на должность выше
    role_list = await get_approver_employees_telegram_id(role)

    for tele_id in role_list:
        await bot.send_message(chat_id=tele_id,
                               text=message,
                               reply_markup=get_access_confirmation(key))

    msg_for_new_user = lang.greetings.waiting_accept

    await callback.message.edit_text(msg_for_new_user)


@general.callback_query(F.data.startswith('access_'))
async def get_accept_by_new_user(callback: CallbackQuery, user: UserContext):
    await callback.answer()
    callback_data = callback.data.split("_")
    action = callback_data[1]

    key = callback_data[2]
    print(f" key: {key}")
    new_user_data = await get_temp_data(key)

    print(f"type: {new_user_data}")
    print(f"data: {new_user_data}")

    if not new_user_data:
        await callback.answer("Ошибка: нет данных о пользователе.")
        print(f"new_user object: {new_user_data}")
        return

    telegram_id: int = new_user_data.get("telegram_id")
    first_name = new_user_data.get("first_name")
    user_role = new_user_data.get("role")

    if not new_user_data:
        await callback.answer("Ошибка: нет данных о пользователе.")
        print(f"new_user object: {new_user_data}")
        return
    match action:
        case "accept":
            senior_telegram_id = callback.from_user.id

            await add_employee(telegram_id=telegram_id,
                               first_name=first_name,
                               role=user_role)

            await add_employee_approval(senior_telegram_id, telegram_id)

            await callback.answer("Пользователь успешно подтверждён!")
            lang_by_new_user = UserContext(telegram_id).lang
            await bot.send_message(chat_id=telegram_id,
                                   text="Ваша заявка принята",
                                   reply_markup=ui_buttons_for_role(user.get_role(), lang_by_new_user))

        case "reject":
            await callback.answer("Пользователь отклонён!")
            await bot.send_message(chat_id=telegram_id,
                                   text="Ваша заявка отклонена")


@general.callback_query(F.data.startswith('lang_'))
async def get_selected_language(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = UserContext(user_id)
    selected_language = F.data.split("_")[1]
    await user.update_lang(lang_code=selected_language)
    lang = user.lang
    await callback.answer(lang.language.accept_lang)


# Автопарк сотрудников
@general.callback_query(F.data.startswith('my_park_'))
async def my_park_actions(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[2]
    employer_id = callback.from_user.id
    await callback.answer()
    match action:
        case "list":
            car_list = await get_employer_car(employer_id)
            text = ''
            for car in car_list:
                car_id = car.get("car_id")
                car_data = f"""{car.get("car_brand")}, {car.get("car_model")}\n
                                {car.get("license_plate")},\n
                                {car.get("technical_inspection")},\n
                                {car.get("insurance")}"""
                text.join(car_data + "\n\n")
                await callback.message.answer(text, reply_markup=car_employer_menu_kb(car_id))

        case "add":
            text = (f"Запиши через запятую данные машины:\n"
                    f"(марка, модель, номерной знак, дата окончания тех. осмотра(день.месяц.год), "
                    f"дата окончания страховки(день.месяц.год)):\n")
            await callback.message.answer(text)
            await state.set_state(EmployerState.waiting_new_car)


@general.message(EmployerState.waiting_new_car)
async def employer_car_info(message: Message, state: FSMContext):
    await state.clear()
    car_data = message.text.split(",")
    data = {
        "brand": car_data[0],
        "model": car_data[1],
        "license_plate": car_data[2],
        "tech_date": car_data[3],
        "ins_date": car_data[4],
    }
    is_text_status = validate_car_data("employer", data).get("status")

    if is_text_status == "ok":
        brand, model, plate, tech_date, ins_date = data
        employer_id = message.from_user.id
        result = await add_employer_car(employer_id, brand, model, plate, tech_date, ins_date)
        status = result.get("status")
        await message.answer(status)

    else:
        await message.answer(f"Error: {is_text_status}")
        text = (f"Запиши через запятую данные машины:\n"
                f"(марка, модель, номерной знак, дата окончания тех. осмотра(день.месяц.год), "
                f"дата окончания страховки(день.месяц.год)):\n")
        await message.answer(text)
        await state.set_state(EmployerState.waiting_new_car)


# Действия для всех машин работника
@general.callback_query(F.data.startswith('car_employer_'))  # Задублированный callback
async def my_park_actions(callback: CallbackQuery):
    action = callback.data.split("_")[-1]
    employer_id = callback.from_user.id
    await callback.answer()
    match action:
        case "edit":
            pass
        case "delete":
            car_id = int(callback.data.split("_")[2])
            result = delete_employer_car_by_id(car_id, employer_id)
            if result:
                await callback.message.answer("Авто было удалено!")
            else:
                await callback.message.answer("Возникла проблема обратитесь в support!")


# Действия с конкретной машиной работника
@general.callback_query(F.data.startswith('car_employer_'))  # Задублированный callback
async def my_park_actions(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    actions = {"plate": "Номерного знака", "inspection": "Техосмотра", "insurance": "Страховки"}
    action = callback.data.split("_")[-1]
    car_id = callback.data.split("_")[2]
    car = {"action": action, "car_id": car_id}
    await state.update_data(car=car)
    await callback.message.answer(f"Введите новые данные для {actions[action]}")
    await state.set_state(EmployerState.new_data_for_car)


@general.message(EmployerState.waiting_new_car)
async def employer_car_info(message: Message, state: FSMContext, user: UserContext):
    actions = {"plate": "license_plate", "inspection": "technical_inspection", "insurance": "insurance"}
    role = user.role
    data = await state.get_data()
    text = message.text
    car = data.get("car")
    car_id = car.get("car_id")
    action = car.get("action")
    if action == "plate":
        if is_likely_license_plate(text):
            result = await edit_car_info(actions.get(action), text, car_id)
            if result > 0:
                await message.answer(f"Номерной знак изменен на {text}", reply_markup=menu_by_role(role))

            await message.answer(f"Это не похоже на известные мне виды номеров повторите ввод")
            await state.clear()
            await state.set_state(EmployerState.new_data_for_car)

    else:
        if is_date(text):
            result = await edit_car_info(actions.get(action), text, car_id)
            if result > 0:
                await message.answer(f"Номерной знак изменен на {text}", reply_markup=menu_by_role(role))

            await message.answer("Вы ввели неподходящие значения даты, нужно так: Д.М.Г")
            await state.clear()
            await state.set_state(EmployerState.new_data_for_car)

    await state.clear()
