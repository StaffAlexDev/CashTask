from database.settings_pg import get_db_connection


async def add_task(assigned_to: int, assigned_by: int, description: str, status: str = 'in_progress'):
    conn = await get_db_connection()
    try:
        await conn.execute(
            '''
            INSERT INTO tasks (assigned_to, assigned_by, description, status)
            VALUES ($1, $2, $3, $4)
            ''',
            assigned_to, assigned_by, description, status
        )
    finally:
        await conn.close()


async def get_employee_tasks(employee_id: int) -> list[dict]:
    conn = await get_db_connection()
    try:
        rows = await conn.fetch(
            'SELECT * FROM tasks WHERE assigned_to = $1', employee_id
        )
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def update_task_status(task_id: int, new_status: str):
    conn = await get_db_connection()
    try:
        await conn.execute(
            'UPDATE tasks SET status = $1, updated_at = CURRENT_TIMESTAMP WHERE task_id = $2',
            new_status, task_id
        )
    finally:
        await conn.close()


async def get_all_tasks(assigned_to: int = None) -> list[dict]:
    conn = await get_db_connection()
    try:
        if assigned_to:
            rows = await conn.fetch('SELECT * FROM tasks WHERE assigned_to = $1', assigned_to)
        else:
            rows = await conn.fetch('SELECT * FROM tasks')
        return [dict(row) for row in rows]
    finally:
        await conn.close()