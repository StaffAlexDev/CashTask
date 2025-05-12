from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.employees_pg import get_employer_car, add_employer_car, delete_employer_car_by_id, edit_car_info
from database.state_models import UserContext, EmployerState
from handlers.general import general
from keyboards.other import car_employer_menu_kb, common_kb_by_role
from utils import validate_car_data, is_likely_license_plate, is_date

worker = Router()


@general.callback_query(F.data.startswith('my_park_'))
async def my_park_actions(callback: CallbackQuery, state: FSMContext, user: UserContext):
    action = callback.data.split("_")[2]
    employer_id = user.telegram_id
    lang = user.lang
    await callback.answer()
    match action:
        case "list":  # ПЕРЕПИСАТЬ ПОД ЛОГИКУ ПАГИНАТОЦИИ
            car_list = await get_employer_car(employer_id)
            text = ''
            for car in car_list:
                car_id = car.get("car_id")
                car_data = f"""{car.get("car_brand")}, {car.get("car_model")}\n
                                {car.get("license_plate")},\n
                                {car.get("technical_inspection")},\n
                                {car.get("insurance")}"""
                text.join(car_data + "\n\n")
                await callback.message.answer(text,
                                              reply_markup=car_employer_menu_kb(car_id, user.lang))

        case "add":
            text = lang.employers.get_new_car
            await callback.message.answer(text)
            await state.set_state(EmployerState.waiting_add_car)


@general.message(EmployerState.waiting_add_car)
async def employer_add_car(message: Message, state: FSMContext, user: UserContext):

    lang = user.lang
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
        await state.clear()
        brand, model, plate, tech_date, ins_date = data
        employer_id = message.from_user.id
        result = await add_employer_car(employer_id, brand, model, plate, tech_date, ins_date)
        status = result.get("status")
        await message.answer(status)

    else:
        await message.answer(f"Error: {is_text_status}")
        text = lang.employers.get_new_car
        await message.answer(text)
        await state.set_state(EmployerState.waiting_add_car)


@general.callback_query(F.data.startswith('car_employer_manage_'))  # Задублированный callback
async def manage_car(callback: CallbackQuery):
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


@general.callback_query(F.data.startswith('car_employer_update_'))  # Задублированный callback
async def update_car_field(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    actions = {"plate": "Номерного знака", "inspection": "Техосмотра", "insurance": "Страховки"}
    action = callback.data.split("_")[-1]
    car_id = callback.data.split("_")[2]
    car = {"action": action, "car_id": car_id}
    await state.update_data(car=car)
    await callback.message.answer(f"Введите новые данные для {actions[action]}")
    await state.set_state(EmployerState.waiting_update_car)


@general.message(EmployerState.waiting_update_car)
async def update_car_info(message: Message, state: FSMContext, user: UserContext):
    actions = {"plate": "license_plate", "inspection": "technical_inspection", "insurance": "insurance"}

    role = user.role
    lang = user.lang
    data = await state.get_data()
    text = message.text
    car = data.get("car")
    car_id = car.get("car_id")
    action = car.get("action")

    if action == "plate":
        if is_likely_license_plate(text):
            result = await edit_car_info(actions.get(action), text, car_id)
            if result > 0:
                await message.answer(f"Номерной знак изменен на {text}",
                                     reply_markup=common_kb_by_role("main_menu", lang, role))
                return

            await message.answer(f"Это не похоже на известные мне виды номеров повторите ввод")
            await state.clear()
            await state.set_state(EmployerState.waiting_update_car)

    else:
        if is_date(text):
            result = await edit_car_info(actions.get(action), text, car_id)
            if result > 0:
                await message.answer(f"Номерной знак изменен на {text}",
                                     reply_markup=common_kb_by_role("main_menu", lang, role))
                return

            await message.answer("Вы ввели неподходящие значения даты, нужно так: Д.М.Г")
            await state.clear()
            await state.set_state(EmployerState.waiting_update_car)

    await state.clear()
