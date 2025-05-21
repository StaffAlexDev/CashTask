from asyncpg import UniqueViolationError

from database.settings_pg import get_db_connection
from utils.random_gen import generate_invite_code


async def add_company(name: str) -> tuple[int, str]:
    """
    Добавляет новую компанию с уникальным invite_code.
    Возвращает кортеж (company_id, invite_code).
    """
    conn = await get_db_connection()
    try:
        for _ in range(10):
            code = generate_invite_code()
            try:
                row = await conn.fetchrow(
                    """
                    INSERT INTO companies(name, invite_code)
                    VALUES($1, $2)
                    RETURNING company_id, invite_code
                    """,
                    name, code
                )
                return row['company_id'], row['invite_code']

            except UniqueViolationError:
                # если код уже занят, повторная генерация
                continue
        raise RuntimeError("Не удалось сгенерировать уникальный invite_code")
    finally:
        await conn.close()


async def get_company_by_code(
    invite_code: str,
) -> dict:
    """
    Ищет и возвращает компанию по ее уникальному ключу
    """
    conn = await get_db_connection()
    try:
        row = await conn.fetch(
            'SELECT name FROM companies WHERE invite_code = $1',
            invite_code
        )
        return dict(row)
    finally:
        await conn.close()


async def get_company_by_id(
    company_id: int,
) -> list:
    """
    Ищет и возвращает компанию по ее сотруднику
    """
    conn = await get_db_connection()
    try:
        row = await conn.fetch(
            'SELECT name, invite_code FROM companies WHERE company_id = $1',
            company_id
        )
        return list(row)
    finally:
        await conn.close()

