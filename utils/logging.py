# import logging
# from pathlib import Path
# from aiogram import Router, types
#
# from utils.enums import Role
# from database.state_models import UserContext
#
# router = Router(name="log_edited")
#
# # === НАСТРОЙКА ЛОГГЕРА ===
# LOG_DIR = Path("logs")
# LOG_DIR.mkdir(exist_ok=True)
#
# log_file = LOG_DIR / "edited_messages.log"
#
# logging.basicConfig(
#     filename=log_file,
#     level=logging.INFO,
#     format="[%(asctime)s] UserID: %(user_id)s | Name: %(user_name)s | Role: %(role)s "
#            "| ChatID: %(chat_id)s | EDITED MESSAGE →\nOLD: %(old_text)s\nNEW: %(message)s\n",
#     datefmt="%Y-%m-%d %H:%M:%S"
# )
#
# logger = logging.getLogger("edited_logger")
#
# # === КЭШ старых сообщений (in-memory) ===
# message_cache = {}
#
#
# # === ХЭНДЛЕР Обычных сообщений (запоминаем старое сообщение) ===
# @router.message()
# async def cache_user_message(message: types.Message, user: UserContext, role: Role):
#     """
#     Сохраняет обычные сообщения пользователей в кэш.
#     """
#     message_cache[message.message_id] = message.text or "[EMPTY MESSAGE]"
#
#
# # === ХЭНДЛЕР Изменённых сообщений (логируем ДО и ПОСЛЕ) ===
# @router.edited_message()
# async def log_edited_message(message: types.Message, user: UserContext, role: Role):
#     """
#     Логирует изменённые сообщения пользователей с показом старого текста.
#     """
#
#     # Получаем имя пользователя
#     full_name = message.from_user.full_name or "Unknown"
#
#     # Получаем новый текст (на всякий случай, если None)
#     new_text = message.text or "[EMPTY MESSAGE]"
#
#     # Получаем старый текст из кэша (если был)
#     old_text = message_cache.get(message.message_id, "[NO DATA]")
#
#     logger.info(
#         new_text,
#         extra={
#             "user_id": user.telegram_id,
#             "user_name": full_name,
#             "role": role.value,
#             "chat_id": message.chat.id,
#             "old_text": old_text,
#         }
#     )
#
#     # Обновляем кэш на новый текст
#     message_cache[message.message_id] = new_text
