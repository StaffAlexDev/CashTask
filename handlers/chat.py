from datetime import datetime
from pathlib import Path

from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.state_models import FinanceStates
from settings import INVOICE_PATTERN
from utils import get_month_year_folder

chat = Router()


@chat.message(F.chat.type.in_(ChatType.GROUP), F.text.as_("text"))
async def handle_group_messages(message: Message, state: FSMContext):
    text = message.text
    match = INVOICE_PATTERN.match(text)

    if match:
        amount = int(text.split()[0])
        await state.update_data(amount=amount)
        await state.set_state(FinanceStates.waiting_for_photo)
        await message.answer("✅ Шаблон верный! Теперь отправьте фото или несколько фото.")


@chat.message(F.chat.type.in_(ChatType.GROUP), FinanceStates.waiting_for_photo, F.photo)
async def caught_photo(message: Message, state: FSMContext):
    try:
        folder_path = get_month_year_folder()

        photo = message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)

        current_time = datetime.now().strftime("%m-%d_%H-%M-%S")
        data = await state.get_data()
        amount = data['amount']
        save_filename = f"{current_time}_sum_{amount}.jpg"
        save_path = Path(folder_path) / save_filename

        await message.bot.download_file(file_info.file_path, str(save_path))
        await message.answer("📸 Фото сохранено!")

    except Exception as e:
        await message.answer(f"❌ Ошибка при сохранении: {str(e)}")

    await state.clear()
