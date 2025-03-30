import os
import re

from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.state_models import TransactionState

PHOTOS_DIR = os.path.join(os.path.dirname(__file__), "..", "photos")
chat = Router()


@chat.message(F.chat.type.in_(ChatType.GROUP), F.text.as_("text"))
async def handle_group_messages(message: Message, state: FSMContext):
    pattern = re.compile(r"(-?\d{1,5})\s+(расход|приход)\s*,?\s*(.+)", re.IGNORECASE)
    text = message.text
    match = pattern.match(text)
    if not match:
        await message.reply("Вы отправили некорректную запись!\nШаблон:\n"
                            "сумма приход/расход, описание")
    else:
        await message.answer("✅ Шаблон верный! Теперь отправьте фото или несколько фото.")
        await state.set_state(TransactionState.waiting_for_photo)


@chat.message(TransactionState.waiting_for_photo, F.photo)
async def caught_photo(message: Message, state: FSMContext):
    # Создаем папку, если её нет
    os.makedirs(PHOTOS_DIR, exist_ok=True)

    photo_id = message.photo[-1].file_id
    file_info = await message.bot.get_file(photo_id)
    file_path = file_info.file_path

    # Сохраняем фото
    save_path = os.path.join(PHOTOS_DIR, f"{photo_id}.jpg")
    await message.bot.download_file(file_path, save_path)

    await message.answer("📸 Фото сохранено!")
    await state.clear()
