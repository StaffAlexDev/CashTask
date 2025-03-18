# import os
# import sys

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from handlers.admins import admin_router
from handlers.workers import workers_router
from handlers.superuser import service_router
from handlers.general import general

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.include_router(admin_router)
dp.include_router(workers_router)
dp.include_router(service_router)
dp.include_router(general)
