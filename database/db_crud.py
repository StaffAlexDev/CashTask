from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from database.db_settings import get_db_connection
from utils import dict_factory


# ========== Employees (Сотрудники) ==========
def add_employee(telegram_id: int, first_name: str, last_name: str, role: str,
                 phone_number: str = None, language: str = None):
    """Добавление сотрудника"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO employees (telegram_id, first_name, last_name, role, phone_number, language) '
            'VALUES (?, ?, ?, ?, ?, ?)',
            (telegram_id, first_name, last_name, role, phone_number, language)
        )
        conn.commit()


def get_employee_by_telegram_id(telegram_id: int):
    """Получение сотрудника по telegram_id"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM employees WHERE telegram_id = ?', (telegram_id,))
        return cursor.fetchone()


def update_employee_role(telegram_id: int, new_role: str):
    """Обновление роли сотрудника"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE employees SET role = ? WHERE telegram_id = ?',
            (new_role, telegram_id)
        )
        conn.commit()


def get_role_by_telegram_id(telegram_id: int):
    """Получение роли сотрудника по telegram_id"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT role FROM employees WHERE telegram_id = ?', (telegram_id,))
        return cursor.fetchone()


# ========== Employee Approvals (Подтверждения сотрудников) ==========
def add_employee_approval(approver_id: int, approved_id: int):
    """Добавление подтверждения сотрудника"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO employee_approvals (approver_id, approved_id) VALUES (?, ?)',
            (approver_id, approved_id)
        )
        conn.commit()


def get_approved_employees(approver_id: int):
    """Получение списка подтвержденных сотрудников"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.* 
            FROM employees e
            JOIN employee_approvals a ON e.telegram_id = a.approved_id
            WHERE a.approver_id = ?
        """, (approver_id,))
        return cursor.fetchall()


# ========== Clients (Клиенты) ==========
def add_client(first_name: str, last_name: str, phone_number: str, social_network: int = None):
    """Добавление клиента"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO clients (first_name, last_name, phone_number, social_network) '
            'VALUES (?, ?, ?, ?)',
            (first_name, last_name, phone_number, social_network)
        )
        conn.commit()


def get_client_by_phone_number(phone_number: str):
    """Получение клиента по telegram_id"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clients WHERE phone_number = ?', (phone_number,))
        return cursor.fetchone()


# ========== Cars (Автомобили) ==========
def add_car(client_id: int, car_brand: str, car_model: str, car_year: int, license_plate: str, vin_code: str = None):
    """Добавление автомобиля"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO cars (clients_id, car_brand, car_model, car_year, license_plate, vin_code) '
            'VALUES (?, ?, ?, ?, ?, ?)',
            (client_id, car_brand, car_model, car_year, license_plate, vin_code)
        )
        conn.commit()


def get_client_cars(client_id: int):
    """Получение автомобилей клиента"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cars WHERE clients_id = ?', (client_id,))
        return cursor.fetchall()


def get_car_by_id(car_id: int):
    """Получение автомобиля по ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cars WHERE car_id = ?', (car_id,))
        return cursor.fetchone()


# ========== Orders (Заказы) ==========
def add_order(car_id: int, worker_id: int, description: str, status: str = 'new'):
    """Добавление заказа"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO orders (car_id, worker_id, description, status) '
            'VALUES (?, ?, ?, ?)',
            (car_id, worker_id, description, status)
        )
        conn.commit()


def get_orders_by_worker(worker_id: int):
    """Получение заказов по ID сотрудника"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.*, c.car_brand, c.car_model, c.license_plate 
            FROM orders o
            JOIN cars c ON o.car_id = c.car_id
            WHERE o.worker_id = ?
        """, (worker_id,))
        return cursor.fetchall()


def update_order_status(order_id: int, new_status: str):
    """Обновление статуса заказа"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE orders SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE order_id = ?',
            (new_status, order_id)
        )
        conn.commit()


# ========== Finances (Финансы) ==========
def add_finance_by_car(amount: float, finance_type: str, description: str, admin_id: int,
                       order_id: int = None, photo: str = None):
    """Добавление финансовой записи по автомобилю"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO finances_by_car (amount, type, description, admin_id, order_id, photo) '
            'VALUES (?, ?, ?, ?, ?, ?)',
            (amount, finance_type, description, admin_id, order_id, photo)
        )
        conn.commit()


def add_finance_general(amount: float, finance_type: str, description: str, admin_id: int, photo: str = None):
    """Добавление общей финансовой записи"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO finances_general (amount, type, description, admin_id, photo) '
            'VALUES (?, ?, ?, ?, ?)',
            (amount, finance_type, description, admin_id, photo)
        )
        conn.commit()


def get_finances_by_order(order_id: int):
    """Получение финансовых записей по заказу"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM finances_by_car WHERE order_id = ?', (order_id,))
        return cursor.fetchall()


def get_financial_report(period: str = 'all') -> dict[str, float | list[dict]]:
    """
    Генерирует финансовый отчет за указанный период с точной обработкой месяцев
    :param period: 'day', 'week', 'two_weeks', 'month', 'all'
    :return: Словарь с отчетом
    """
    # Определяем дату начала периода
    now = datetime.now()
    period_map = {
        'day': (now - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
        'week': (now - timedelta(weeks=1)).strftime('%Y-%m-%d %H:%M:%S'),
        'two_weeks': (now - timedelta(weeks=2)).strftime('%Y-%m-%d %H:%M:%S'),
        'month': (now - relativedelta(months=1)).strftime('%Y-%m-%d %H:%M:%S'),
        'all': None
    }

    if period not in period_map:
        raise ValueError(f"Недопустимый период. Доступны: {list(period_map.keys())}")

    # Формируем условие для фильтрации по дате
    date_condition = ""
    if period != 'all':
        start_date = period_map[period]
        date_condition = f"WHERE created_at >= '{start_date}'"

    with get_db_connection() as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        # 1. Общая сводка по типам операций
        query = f"""
            SELECT 
                type,
                SUM(amount) as total_amount,
                COUNT(*) as count
            FROM (
                SELECT type, amount, created_at FROM finances_by_car
                UNION ALL
                SELECT type, amount, created_at FROM finances_general
            )
            {date_condition}
            GROUP BY type
        """
        cursor.execute(query)
        summary = cursor.fetchall()

        # 2. Детализированные записи с сортировкой по дате
        detail_query = f"""
            SELECT 
                'by_car' as source,
                amount,
                type,
                description,
                strftime('%Y-%m-%d %H:%M:%S', created_at) as created_at,
                order_id
            FROM finances_by_car
            {date_condition}

            UNION ALL

            SELECT 
                'general' as source,
                amount,
                type,
                description,
                strftime('%Y-%m-%d %H:%M:%S', created_at) as created_at,
                NULL as order_id
            FROM finances_general
            {date_condition}

            ORDER BY created_at DESC
        """
        cursor.execute(detail_query)
        transactions = cursor.fetchall()

        # 3. Расчет итогов
        total_income = sum(t['total_amount'] for t in summary if t['type'] == 'income')
        total_expense = sum(t['total_amount'] for t in summary if t['type'] == 'expense')

        return {
            'period': period,
            'start_date': period_map.get(period, 'all time'),
            'end_date': now.strftime('%Y-%m-%d %H:%M:%S'),
            'total_income': total_income,
            'total_expense': total_expense,
            'profit': total_income - total_expense,
            'summary': summary,
            'transactions': transactions
        }


# ========== Tasks (Задачи) ==========
def add_task(assigned_to: int, assigned_by: int, description: str, status: str = 'in_progress'):
    """Добавление задачи"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO tasks (assigned_to, assigned_by, description, status) '
            'VALUES (?, ?, ?, ?)',
            (assigned_to, assigned_by, description, status)
        )
        conn.commit()


def get_employee_tasks(employee_id: int):
    """Получение задач сотрудника"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE assigned_to = ?', (employee_id,))
        return cursor.fetchall()


def update_task_status(task_id: int, new_status: str):
    """Обновление статуса задачи"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE task_id = ?',
            (new_status, task_id)
        )
        conn.commit()


if __name__ == '__main__':
    # Примеры использования
    add_employee(123456789, 'Иван', 'Иванов', 'mechanic', '+79123456789')
    employee = get_employee_by_telegram_id(123456789)
    print(employee)
