from datetime import datetime
from database.settings_pg import get_db_connection
from utils.enums import Role


async def add_employee(company_id: int, telegram_id: int, first_name: str, role: str):
    conn = await get_db_connection()
    try:
        await conn.execute(
            '''
            INSERT INTO employees (company_id, telegram_id, first_name, role)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (telegram_id, company_id) DO NOTHING
            ''',
            company_id, telegram_id, first_name, role
        )
    finally:
        await conn.close()


async def get_employee_by_telegram_id(company_id: int, telegram_id: int) -> dict:
    conn = await get_db_connection()
    try:
        row = await conn.fetchrow(
            'SELECT * FROM employees WHERE company_id = $1 AND telegram_id = $2',
            company_id, telegram_id
        )
        return dict(row) if row else {}
    finally:
        await conn.close()


async def update_employee_role(company_id: int, telegram_id: int, new_role: Role):
    conn = await get_db_connection()
    try:
        await conn.execute(
            'UPDATE employees SET role = $1 WHERE company_id = $2 AND telegram_id = $3',
            new_role.value, company_id, telegram_id
        )
    finally:
        await conn.close()


async def get_role_by_telegram_id(company_id: int, telegram_id: int):
    conn = await get_db_connection()
    try:
        row = await conn.fetchrow(
            'SELECT role FROM employees WHERE company_id = $1 AND telegram_id = $2',
            company_id, telegram_id
        )
        return row['role'] if row else None
    finally:
        await conn.close()


async def add_employee_approval(company_id: int, approver_id: int, approved_id: int):
    conn = await get_db_connection()
    try:
        await conn.execute(
            '''
            INSERT INTO employee_approvals (company_id, approver_id, approved_id)
            VALUES ($1, $2, $3)
            ON CONFLICT (company_id, approver_id, approved_id) DO NOTHING
            ''',
            company_id, approver_id, approved_id
        )
    finally:
        await conn.close()


async def get_approved_employees(company_id: int, approver_id: int) -> list:
    conn = await get_db_connection()
    try:
        rows = await conn.fetch(
            '''
            SELECT e.*
            FROM employees e
            JOIN employee_approvals a
              ON e.company_id = a.company_id
             AND e.telegram_id = a.approved_id
            WHERE a.company_id = $1 AND a.approver_id = $2
            ''',
            company_id, approver_id
        )
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def get_approver_employees_telegram_id(company_id: int, role: Role, exclude_id: int) -> list[int]:
    conn = await get_db_connection()
    try:
        for upper_role in Role.get_upper_roles(role):
            rows = await conn.fetch(
                '''
                SELECT telegram_id
                  FROM employees
                 WHERE company_id = $1
                   AND role = $2
                   AND telegram_id != $3
                ''',
                company_id, upper_role.value, exclude_id
            )
            if rows:
                return [r['telegram_id'] for r in rows]
        return []
    finally:
        await conn.close()


async def get_employer_car(company_id: int, employer_id: int) -> list:
    conn = await get_db_connection()
    try:
        rows = await conn.fetch(
            'SELECT * FROM employer_cars WHERE company_id = $1 AND employer_id = $2',
            company_id, employer_id
        )
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def add_employer_car(company_id: int, employer_id: int, car_brand: str, car_model: str,
                           license_plate: str, technical_inspection: datetime, insurance: datetime) -> dict:
    conn = await get_db_connection()
    try:
        existing = await conn.fetchrow(
            'SELECT 1 FROM employer_cars WHERE company_id = $1 AND employer_id = $2 AND license_plate = $3',
            company_id, employer_id, license_plate
        )
        if existing:
            return {"status": "car_is_exist"}

        await conn.execute(
            '''
            INSERT INTO employer_cars (company_id, employer_id, car_brand, 
            car_model, license_plate, technical_inspection, insurance)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ''',
            company_id, employer_id, car_brand, car_model, license_plate, technical_inspection, insurance
        )
        return {"status": "Авто добавлено!"}
    except Exception as e:
        return {"status": "error", "message": f"Ошибка при добавлении: {e}"}
    finally:
        await conn.close()


async def get_employees_cars(company_id: int) -> list:
    conn = await get_db_connection()
    try:
        rows = await conn.fetch(
            'SELECT * FROM employer_cars WHERE company_id = $1',
            company_id
        )
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def get_all_employees(company_id: int, role: str = None) -> list[dict]:
    conn = await get_db_connection()
    try:
        if role:
            rows = await conn.fetch(
                'SELECT * FROM employees WHERE company_id = $1 AND role = $2',
                company_id, role
            )
        else:
            rows = await conn.fetch(
                'SELECT * FROM employees WHERE company_id = $1',
                company_id
            )
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def edit_car_info(company_id: int, action: str, new_data, car_id: int) -> int:
    conn = await get_db_connection()
    try:
        query = f"UPDATE employer_cars SET {action} = $1 WHERE company_id = $2 AND car_id = $3"
        result = await conn.execute(query, new_data, company_id, car_id)
        return int(result.split()[-1])
    finally:
        await conn.close()


async def delete_car_by_id(company_id: int, car_id: int, deleted_by: int) -> bool:
    conn = await get_db_connection()
    try:
        result = await conn.execute(
            'UPDATE cars SET is_deleted = TRUE WHERE company_id = $1 AND car_id = $2',
            company_id, car_id
        )
        count = int(result.split()[1])
        if count > 0:
            await conn.execute(
                'INSERT INTO deletion_logs (item_type, item_id, deleted_by) VALUES ($1, $2, $3)',
                'car', car_id, deleted_by
            )
            return True
        return False
    finally:
        await conn.close()


async def delete_employer_car_by_id(company_id: int, car_id: int, employer_id: int) -> bool:
    conn = await get_db_connection()
    try:
        result = await conn.execute(
            'DELETE FROM employer_cars WHERE company_id = $1 AND car_id = $2 AND employer_id = $3',
            company_id, car_id, employer_id
        )
        return int(result.split()[-1]) > 0
    finally:
        await conn.close()
