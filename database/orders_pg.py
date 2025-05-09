from database.settings_pg import get_db_connection


async def add_order(car_id: int, description: str, status: str = 'new', worker_id: int = None):
    conn = await get_db_connection()
    try:
        await conn.execute(
            '''INSERT INTO orders (car_id, description, status, worker_id)
               VALUES ($1, $2, $3, $4)''',
            car_id, description, status, worker_id
        )
    finally:
        await conn.close()


async def get_orders_by_worker(worker_id: int):
    conn = await get_db_connection()
    try:
        rows = await conn.fetch(
            '''
            SELECT o.*, c.car_brand, c.car_model, c.license_plate 
            FROM orders o
            JOIN cars c ON o.car_id = c.car_id
            WHERE o.worker_id = $1
            ''', worker_id
        )
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def update_order_status(order_id: int, new_status: str):
    conn = await get_db_connection()
    try:
        await conn.execute(
            '''
            UPDATE orders SET status = $1, updated_at = CURRENT_TIMESTAMP
            WHERE order_id = $2
            ''', new_status, order_id
        )
    finally:
        await conn.close()


async def get_all_orders(status: str = None) -> list[dict]:
    conn = await get_db_connection()
    try:
        if status:
            rows = await conn.fetch('SELECT * FROM orders WHERE status = $1', status)
        else:
            rows = await conn.fetch('SELECT * FROM orders')
        return [dict(row) for row in rows]
    finally:
        await conn.close()
