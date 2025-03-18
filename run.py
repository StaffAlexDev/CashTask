# import sys
# import os
import asyncio

from database.struct_db import create_tables
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from routers import dp
from settings import bot


async def on_startup():
    create_tables()
    print('The bot went online')
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.run(on_startup())
