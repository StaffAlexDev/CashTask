from enum import Enum
from database.struct_db import get_db_connection


# Добавление пользователя
def add_employees(telegram_id: int, first_name: str, last_name: str, role: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()

        sql = 'SELECT * FROM employees WHERE telegram_id = ?'
        cursor.execute(sql, (telegram_id,))
        if cursor.fetchone() is not None:
            print("Пользователь уже существует")
            return
        cursor.execute(
            'INSERT INTO employees (telegram_id, first_name, last_name, role) VALUES (?, ?, ?, ?, ?)',
            (telegram_id, first_name, last_name, role)
        )
        conn.commit()


# Получение пользователя по telegram_id
def get_user_by_telegram_id(telegram_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        curr_user = cursor.fetchone()
        return curr_user


def get_approvers_for_role(user_role):
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT access_level FROM roles WHERE role_name = ?", (user_role,))
        role_level = cursor.fetchone()

        if not role_level:
            return []

        access_level = role_level[0]

        cursor.execute("""
            SELECT u.telegram_id 
            FROM users u
            JOIN roles r ON u.role_id = r.role_id
            WHERE r.access_level = ?;
        """, (access_level + 1,))

        approvers = cursor.fetchall()
        return [user[0] for user in approvers]


# Подтверждение пользователя
def approve_user(approver_telegram_id, approved_telegram_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO approvals (approver_id, approved_id)
            VALUES (?, ?);
        """, (approver_telegram_id, approved_telegram_id))
        conn.commit()


# Посмотреть кого подтвердил конкретный пользователь
def get_approved_users(approver_telegram_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.telegram_id, u.first_name, u.last_name
            FROM users u
            JOIN approvals a ON u.telegram_id = a.approved_id
            WHERE a.approver_id = ?;
        """, (approver_telegram_id,))
        return cursor.fetchall()


# Посмотреть кто подтвердил конкретного пользователя
def get_approvers_for_user(approved_telegram_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.telegram_id, u.first_name, u.last_name
            FROM users u
            JOIN approvals a ON u.telegram_id = a.approver_id
            WHERE a.approved_id = ?;
        """, (approved_telegram_id,))
        return cursor.fetchall()


# Добавление автомобиля
def add_car(user_id, car_brand, car_model, car_year, license_plate):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO cars (user_id, car_brand, car_model, car_year, license_plate) VALUES (?, ?, ?, ?, ?)',
            (user_id, car_brand, car_model, car_year, license_plate)
        )
        conn.commit()


# Добавление финансовой записи
def add_finance_by_car(amount: int, amount_type: str, description: str, admin_id: int, car_id=None):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if car_id is not None:
            cursor.execute('SELECT * FROM cars WHERE car_id = ?', (car_id,))
            if cursor.fetchone() is None:
                print("Автомобиль не найден")
                return
        cursor.execute(
            'INSERT INTO finances_by_car (amount, description, type, admin_id, car_id) VALUES (?, ?, ?, ?, ?)',
            (amount, description, amount_type, admin_id, car_id)
        )
        conn.commit()
        print(f"Coхранил: {amount}, {description}, {amount_type}, {admin_id}")


def add_finance_by_general(amount: int, amount_type: str, description: str, admin_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO finances_general (amount, type, description, admin_id) VALUES (?, ?, ?, ?, ?)',
            (amount, description, amount_type, admin_id)
        )
        conn.commit()
        print(f"Coхранил: {amount}, {description}, {amount_type}, {admin_id}")


async def add_order(car_id: int, service: str, user_id: int):
    """
    Добавляет заказ в таблицу orders.
    """
    with get_db_connection() as conn:
        try:
            cursor = conn.cursor()
            # Вставляем заказ в таблицу
            cursor.execute("""
                INSERT INTO orders (car_id, service, user_id)
                VALUES (?, ?, ?)
            """, (car_id, service, user_id))

            # Сохраняем изменения
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении заказа: {e}")
            return False


def get_orders_by_worker(worker_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT car_brand, car_model, license_plate, vin_code FROM orders "
                       "WHERE worker_id = ?", (worker_id,))
        result = cursor.fetchall()[0]
        return [car[0] for car in result]


async def get_user_cars(user_id: int):
    """
    Получает список автомобилей пользователя по его user_id.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Выбираем все автомобили пользователя
        cursor.execute("""
            SELECT car_id, car_brand, car_model, car_year, license_plate
            FROM cars
            WHERE user_id = ?
        """, (user_id,))

        # Возвращаем результат в виде списка словарей
        cars = cursor.fetchall()
        return [dict(car) for car in cars]
    except Exception as e:
        print(f"Ошибка при получении автомобилей: {e}")
        return []
    finally:
        conn.close()


def get_orders_in_work():
    with get_db_connection() as conn:
        cursor = conn.cursor()


# Пример использования

if __name__ == '__main__':
    add_employees(123456789, 'Иван', 'Иванов', '+79123456789')
    user1 = get_user_by_telegram_id(123456789)
    print(user1)
