# import os
# import sys

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from handlers.admins import admins
from handlers.chat import chat
from handlers.commands import commands
from handlers.workers import worker
from handlers.superuser import superuser
from handlers.general import general

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.include_router(admins)
dp.include_router(worker)
dp.include_router(superuser)
dp.include_router(general)
dp.include_router(chat)
dp.include_router(commands)
