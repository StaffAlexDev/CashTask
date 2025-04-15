
import asyncio

from bot_menu import set_main_menu
from database.db_crud import insert_test_clients_and_cars
from database.struct_db import create_tables

from routers import dp
from settings import bot


async def on_startup():
    await set_main_menu(bot)
    create_tables()
    insert_test_clients_and_cars()
    print('The bot went online')
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.run(on_startup())
