import json

from database.settings_pg import get_db_connection
from utils.random_gen import generate_temp_key


async def add_temporary_data(data: dict) -> str:
    """Добавление временных данных в базу и генерация случайной строки для ключа"""
    key = generate_temp_key()
    conn = await get_db_connection()
    try:
        await conn.execute(
            '''INSERT INTO temporary_data (key, data) VALUES ($1, $2)''',
            key, data
        )
        return key
    finally:
        await conn.close()


async def get_temporary_data(key: str) -> dict | None:
    conn = await get_db_connection()
    try:
        row = await conn.fetchrow('SELECT data FROM temporary_data WHERE key = $1', key)
        if not row:
            return None
        data = row['data']
        if isinstance(data, dict):
            return data
        return json.loads(data)
    finally:
        await conn.close()
