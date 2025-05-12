from datetime import datetime

from database.settings_pg import get_db_connection
from utils.enums import Role


async def add_employee(telegram_id: int, first_name: str, role: str):
    conn = await get_db_connection()
    try:
        await conn.execute(
            '''
            INSERT INTO employees (telegram_id, first_name, role)
            VALUES ($1, $2, $3)
            ''', telegram_id, first_name, role
        )
    finally:
        await conn.close()


async def get_employee_by_telegram_id(telegram_id: int) -> dict:
    conn = await get_db_connection()
    try:
        row = await conn.fetchrow('SELECT * FROM employees WHERE telegram_id = $1', telegram_id)
        return dict(row) if row else {}
    finally:
        await conn.close()


async def update_employee_role(telegram_id: int, new_role: Role):
    conn = await get_db_connection()
    try:
        await conn.execute(
            'UPDATE employees SET role = $1 WHERE telegram_id = $2',
            new_role.value, telegram_id
        )
    finally:
        await conn.close()


async def get_role_by_telegram_id(telegram_id: int):
    conn = await get_db_connection()
    try:
        row = await conn.fetchrow('SELECT role FROM employees WHERE telegram_id = $1', telegram_id)
        return row['role'] if row else None
    finally:
        await conn.close()


async def add_employee_approval(approver_id: int, approved_id: int):
    conn = await get_db_connection()
    try:
        await conn.execute(
            'INSERT INTO employee_approvals (approver_id, approved_id) VALUES ($1, $2)',
            approver_id, approved_id
        )
    finally:
        await conn.close()


async def get_approved_employees(approver_id: int) -> list:
    conn = await get_db_connection()
    try:
        rows = await conn.fetch(
            '''
            SELECT e.* 
            FROM employees e
            JOIN employee_approvals a ON e.telegram_id = a.approved_id
            WHERE a.approver_id = $1
            ''', approver_id
        )
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def get_approver_employees_telegram_id(role: Role, exclude_id) -> list[int]:
    conn = await get_db_connection()
    try:
        for upper_role in Role.get_upper_roles(role):
            rows = await conn.fetch(
                '''
                SELECT telegram_id
                  FROM employees
                 WHERE role = $1
                   AND telegram_id != $2
                ''',
                upper_role.value,
                exclude_id
            )
            if rows:
                return [r['telegram_id'] for r in rows]
        return []
    finally:
        await conn.close()


async def get_employer_car(employer_id: int) -> list:
    conn = await get_db_connection()
    try:
        rows = await conn.fetch(
            'SELECT * FROM employer_cars WHERE employer_id = $1', employer_id
        )
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def add_employer_car(employer_id: int, car_brand: str, car_model: str, license_plate: str,
                           technical_inspection: datetime, insurance: datetime) -> dict:
    conn = await get_db_connection()
    try:
        car = await conn.fetchrow(
            'SELECT * FROM employer_cars WHERE employer_id = $1 AND license_plate = $2',
            employer_id, license_plate
        )
        if car:
            return {"status": "car_is_exist"}

        await conn.execute(
            '''INSERT INTO employer_cars (employer_id, car_brand, car_model, license_plate,
            technical_inspection, insurance) VALUES ($1, $2, $3, $4, $5, $6)''',
            employer_id, car_brand, car_model, license_plate, technical_inspection, insurance
        )
        return {"status": "Авто добавлено!"}
    except Exception as e:
        return {"status": "error", "message": f"Ошибка при добавлении: {e}"}
    finally:
        await conn.close()


async def get_employees_cars() -> list:
    conn = await get_db_connection()
    try:
        rows = await conn.fetch('SELECT * FROM employer_cars')
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def get_all_employees(role: str = None) -> list[dict]:
    conn = await get_db_connection()
    try:
        if role:
            rows = await conn.fetch('SELECT * FROM employees WHERE role = $1', role)
        else:
            rows = await conn.fetch('SELECT * FROM employees')
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def edit_car_info(action: str, new_data, car_id: int) -> int:
    conn = await get_db_connection()
    try:
        query = f"UPDATE employer_cars SET {action} = $1 WHERE car_id = $2"
        result = await conn.execute(query, new_data, car_id)
        return int(result.split()[-1])
    finally:
        await conn.close()


async def delete_car_by_id(car_id: int, deleted_by: int) -> bool:
    conn = await get_db_connection()
    try:
        result = await conn.execute('UPDATE cars SET is_deleted = TRUE WHERE car_id = $1', car_id)
        if result[-1] != '0':
            await conn.execute(
                'INSERT INTO deletion_logs (item_type, item_id, deleted_by) VALUES ($1, $2, $3)',
                'car', car_id, deleted_by
            )
            return True
        return False
    finally:
        await conn.close()


async def delete_employer_car_by_id(car_id: int, employer_id: int) -> bool:
    conn = await get_db_connection()
    try:
        result = await conn.execute(
            'DELETE FROM employer_cars WHERE car_id = $1 AND employer_id = $2',
            car_id, employer_id
        )
        return result[-1] != '0'
    finally:
        await conn.close()
