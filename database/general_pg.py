
from database.settings_pg import get_db_connection
from utils.random_gen import generate_temp_key


async def add_temporary_data(
    company_id: int,
    data: dict
) -> str:
    """
    Сохраняет временные данные для конкретной компании и возвращает сгенерированный ключ.
    """
    key = generate_temp_key()
    conn = await get_db_connection()
    try:
        await conn.execute(
            '''
            INSERT INTO temporary_data (key, data, company_id)
            VALUES ($1, $2, $3)
            ''',
            key, data, company_id
        )
        return key
    finally:
        await conn.close()


async def get_temporary_data(
    company_id: int,
    key: str
) -> dict | None:
    """
    Возвращает сохранённые ранее временные данные по ключу для данной компании.
    """
    conn = await get_db_connection()
    try:
        row = await conn.fetchrow(
            '''
            SELECT data
            FROM temporary_data
            WHERE company_id = $1 AND key = $2
            ''',
            company_id, key
        )
        return row['data'] if row else None
    finally:
        await conn.close()
