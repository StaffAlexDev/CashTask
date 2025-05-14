from database.settings_pg import get_db_connection


async def add_order(
    company_id: int,
    car_id: int,
    description: str,
    status: str = 'new',
    worker_id: int = None
) -> None:
    """
    Добавляет новый заказ, привязанный к компании.
    """
    conn = await get_db_connection()
    try:
        await conn.execute(
            '''
            INSERT INTO orders (
                company_id, car_id, description, status, worker_id
            ) VALUES ($1, $2, $3, $4, $5)
            ''',
            company_id, car_id, description, status, worker_id
        )
    finally:
        await conn.close()


async def get_orders_by_worker(
    company_id: int,
    worker_id: int
) -> list[dict]:
    """
    Возвращает заказы, назначенные конкретному работнику в компании.
    """
    conn = await get_db_connection()
    try:
        rows = await conn.fetch(
            '''
            SELECT o.*, c.car_brand, c.car_model, c.license_plate
            FROM orders o
            JOIN cars c ON o.car_id = c.car_id AND o.company_id = c.company_id
            WHERE o.company_id = $1 AND o.worker_id = $2
            ORDER BY o.created_at DESC
            ''',
            company_id, worker_id
        )
        return [dict(r) for r in rows]
    finally:
        await conn.close()


async def update_order_status(
    company_id: int,
    order_id: int,
    new_status: str
) -> int:
    """
    Обновляет статус заказа и возвращает число затронутых строк.
    """
    conn = await get_db_connection()
    try:
        result = await conn.execute(
            '''
            UPDATE orders
               SET status = $1,
                   updated_at = CURRENT_TIMESTAMP
             WHERE company_id = $2 AND order_id = $3
            ''',
            new_status, company_id, order_id
        )
        return int(result.split()[-1])
    finally:
        await conn.close()


async def get_all_orders(
    company_id: int,
    status: str = None
) -> list[dict]:
    """
    Возвращает все заказы компании, опционально фильтруя по статусу.
    """
    conn = await get_db_connection()
    try:
        if status:
            rows = await conn.fetch(
                'SELECT * FROM orders WHERE company_id = $1 AND status = $2',
                company_id, status
            )
        else:
            rows = await conn.fetch(
                'SELECT * FROM orders WHERE company_id = $1',
                company_id
            )
        return [dict(r) for r in rows]
    finally:
        await conn.close()
