from enum import Enum
from database.struct_db import get_db_connection


class FinanceType(Enum):
    INCOME = "income"
    EXPENSE = "expense"


# Добавление пользователя
def add_user(telegram_id, first_name, last_name, phone_number, role):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        if cursor.fetchone() is not None:
            print("Пользователь уже существует")
            return
        cursor.execute(
            'INSERT INTO users (telegram_id, first_name, last_name, phone_number, role) VALUES (?, ?, ?, ?, ?)',
            (telegram_id, first_name, last_name, phone_number, role)
        )
        conn.commit()


# Получение пользователя по telegram_id
def get_user_by_telegram_id(telegram_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        curr_user = cursor.fetchone()
        return curr_user


def get_roles():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT role_name FROM roles')
        roles = cursor.fetchall()
        return [role[0] for role in roles][:-1]


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
def add_finance_record(amount, description, amount_type, admin_id, car_id=None):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if car_id is not None:
            cursor.execute('SELECT * FROM cars WHERE car_id = ?', (car_id,))
            if cursor.fetchone() is None:
                print("Автомобиль не найден")
                return
        cursor.execute(
            'INSERT INTO finances (amount, description, type, admin_id, car_id) VALUES (?, ?, ?, ?, ?)',
            (amount, description, amount_type, admin_id, car_id)
        )
        conn.commit()


async def add_order(car_id: int, service: str, user_id: int):
    """
    Добавляет заказ в таблицу orders.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
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
    finally:
        conn.close()


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


# Пример использования
if __name__ == '__main__':
    add_user(123456789, 'Иван', 'Иванов', '+79123456789', 'client')
    user1 = get_user_by_telegram_id(123456789)
    print(user1)
