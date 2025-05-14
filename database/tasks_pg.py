from database.settings_pg import get_db_connection


async def add_task(
    company_id: int,
    assigned_to: int,
    assigned_by: int,
    description: str,
    status: str = 'in_progress'
) -> None:
    """
    Создаёт задачу в контексте компании.
    """
    conn = await get_db_connection()
    try:
        await conn.execute(
            '''
            INSERT INTO tasks (
                company_id, assigned_to, assigned_by, description, status
            ) VALUES ($1, $2, $3, $4, $5)
            ''',
            company_id, assigned_to, assigned_by, description, status
        )
    finally:
        await conn.close()


async def get_employee_tasks(
    company_id: int,
    employee_id: int
) -> list[dict]:
    """
    Возвращает все задачи, назначенные работнику внутри компании.
    """
    conn = await get_db_connection()
    try:
        rows = await conn.fetch(
            'SELECT * FROM tasks WHERE company_id = $1 AND assigned_to = $2',
            company_id, employee_id
        )
        return [dict(r) for r in rows]
    finally:
        await conn.close()


async def update_task_status(
    company_id: int,
    task_id: int,
    new_status: str
) -> int:
    """
    Обновляет статус задачи и возвращает число затронутых строк.
    """
    conn = await get_db_connection()
    try:
        result = await conn.execute(
            '''
            UPDATE tasks
               SET status = $1,
                   updated_at = CURRENT_TIMESTAMP
             WHERE company_id = $2 AND task_id = $3
            ''',
            new_status, company_id, task_id
        )
        return int(result.split()[-1])
    finally:
        await conn.close()


async def get_all_tasks(
    company_id: int,
    assigned_to: int = None
) -> list[dict]:
    """
    Возвращает все задачи компании, опционально фильтруя по исполнителю.
    """
    conn = await get_db_connection()
    try:
        if assigned_to is not None:
            rows = await conn.fetch(
                'SELECT * FROM tasks WHERE company_id = $1 AND assigned_to = $2',
                company_id, assigned_to
            )
        else:
            rows = await conn.fetch(
                'SELECT * FROM tasks WHERE company_id = $1',
                company_id
            )
        return [dict(r) for r in rows]
    finally:
        await conn.close()