from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.finance_pg import add_finance_by_car
from models.state_models import FinanceStates, UserContext
from handlers.admins import admins
from keyboards.other import common_kb_by_role, enum_kb
from utils.enums import Period


@admins.callback_query(F.data.startswith("finance_"))
async def finance_income(callback: CallbackQuery, state: FSMContext, user: UserContext):
    type_finance = callback.data.split("_")[1]
    if type_finance == "report":
        await callback.message.edit_text("Выберите период отчета",
                                         reply_markup=enum_kb(Period.for_ui(), user.lang, "period"))
    else:
        await state.update_data(type_finance=type_finance)
        await callback.message.edit_text("Выберите тип дохода!",
                                         reply_markup=common_kb_by_role("finance_types",
                                                                        user.lang,
                                                                        user.get_role()))
    await callback.answer()


@admins.callback_query(F.data == "from_car")
async def income_from_the_car(callback: CallbackQuery):
    await callback.answer("Дописать НУЖНО ))")


@admins.callback_query(F.data == "general")
async def income_from_the_car(callback: CallbackQuery, state: FSMContext):
    await state.update_data(type_investments=callback.data)
    await state.set_state(FinanceStates.investments)
    await callback.answer()
    await callback.message.edit_text("Введите сумму и описание через запятую:")


@admins.message(FinanceStates.investments)
async def wait_sum(message: Message, state: FSMContext):
    state_data = await state.get_data()
    type_finance = state_data["type_finance"]
    type_investments = state_data["type_investments"]  # TODO перепроверить последовательно состояния
    data = message.text.split(",")
    amount = int(data[0])
    description = data[1]
    admin_id = message.from_user.id
    await add_finance_by_car(amount=amount, finance_type=type_finance, description=description,  admin_id=admin_id)

    print(f"Сумма инвестиции: {amount}, {type_finance}, {description}, {admin_id}")
    await message.edit_text(f"Сумма {amount} сохранена!")
    await state.clear()
