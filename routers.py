
from aiogram import Dispatcher

from handlers.admins import admins
from handlers.employers import worker
from handlers.superuser import superuser
from handlers.general import general
from handlers.chat import chat
from handlers.commands import commands
from handlers.unknown_commands import unknown_cmd

import time
from typing import Optional, Dict, Any
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.base import StorageKey, StateType


class TTLMemoryStorage(MemoryStorage):
    """
    MemoryStorage с TTL: если с момента set_state прошло больше ttl_seconds,
    состояние и данные удаляются автоматически.
    """
    def __init__(self, ttl_seconds: int):
        super().__init__()
        self.ttl = ttl_seconds
        # карта: StorageKey -> время последнего set_state
        self._timestamps: Dict[StorageKey, float] = {}

    async def set_state(
        self,
        key: StorageKey,
        state: StateType = None
    ) -> None:
        await super().set_state(key, state)
        self._timestamps[key] = time.time()

    async def get_state(self, key: StorageKey) -> Optional[str]:
        ts = self._timestamps.get(key)
        if ts is not None and (time.time() - ts) > self.ttl:
            self.storage.pop(key, None)
            self._timestamps.pop(key, None)
            return None
        return await super().get_state(key)

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        ts = self._timestamps.get(key)
        if ts is not None and (time.time() - ts) > self.ttl:
            self.storage.pop(key, None)
            self._timestamps.pop(key, None)
            return {}
        return await super().get_data(key)


storage = TTLMemoryStorage(ttl_seconds=60)

dp = Dispatcher(storage=storage)


dp.include_router(admins)
dp.include_router(worker)
dp.include_router(superuser)
dp.include_router(general)
dp.include_router(chat)
dp.include_router(commands)
dp.include_router(unknown_cmd)
