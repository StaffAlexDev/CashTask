
import asyncio

from bot_menu import set_main_menu
from database.struct_pg import create_tables
from middlewares import setup_middlewares

from routers import dp
from settings import bot


async def on_startup():
    await set_main_menu(bot)
    await create_tables()
    print('The bot went online')
    await bot.delete_webhook(drop_pending_updates=True)
    setup_middlewares(dp)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        # await checking_the_end_date_of_documents()
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(on_startup())
