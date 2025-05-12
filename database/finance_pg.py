from database.settings_pg import get_db_connection
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


async def add_finance_by_car(amount: float, finance_type: str, description: str, admin_id: int,
                             order_id: int = None, photo: str = None):
    conn = await get_db_connection()
    try:
        await conn.execute(
            '''INSERT INTO finances_by_car (amount, type, description, admin_id, order_id, photo)
               VALUES ($1, $2, $3, $4, $5, $6)''',
            amount, finance_type, description, admin_id, order_id, photo
        )
    finally:
        await conn.close()


async def add_finance_general(amount: float, finance_type: str, description: str, admin_id: int, photo: str = None):
    conn = await get_db_connection()
    try:
        await conn.execute(
            '''INSERT INTO finances_general (amount, type, description, admin_id, photo)
               VALUES ($1, $2, $3, $4, $5)''',
            amount, finance_type, description, admin_id, photo
        )
    finally:
        await conn.close()


async def get_finances_by_order(order_id: int):
    conn = await get_db_connection()
    try:
        rows = await conn.fetch('SELECT * FROM finances_by_car WHERE order_id = $1', order_id)
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def get_financial_report(period: str = 'all') -> dict:
    now = datetime.now()
    # 1) Вычисляем start_date
    period_map = {
        'day': now - timedelta(days=1),
        'week': now - timedelta(weeks=1),
        'two_weeks': now - timedelta(weeks=2),
        'month': now - relativedelta(months=1),
        'all': None
    }
    if period not in period_map:
        raise ValueError(f"Недопустимый период. Доступны: {list(period_map.keys())}")
    start_date = period_map[period]

    # 2) Строим условие и базовые params
    if start_date:
        condition = 'WHERE created_at >= $1'
        params = [start_date]
    else:
        condition = ''
        params = []

    conn = await get_db_connection()
    try:
        # 3) Суммарная часть — одинарное использование params
        summary_q = f"""
            SELECT type, SUM(amount) AS total_amount, COUNT(*) AS count
            FROM (
                SELECT type, amount, created_at FROM finances_by_car
                UNION ALL
                SELECT type, amount, created_at FROM finances_general
            )
            {condition}
            GROUP BY type
        """
        summary = await conn.fetch(summary_q, *params)

        # 4) Транзакции — дублируем params ровно дважды
        args = params + params
        transactions_q = f"""
            SELECT 'by_car' AS source, amount, type, description, created_at, order_id
            FROM finances_by_car
            {condition}
            UNION ALL
            SELECT 'general' AS source, amount, type, description, created_at, NULL AS order_id
            FROM finances_general
            {condition}
            ORDER BY created_at DESC
        """
        transactions = await conn.fetch(transactions_q, *args)

        # 5) Подсчёт итогов
        total_income = sum(r['total_amount'] for r in summary if r['type'] == 'income')
        total_expense = sum(r['total_amount'] for r in summary if r['type'] == 'expense')

        return {
            'period': period,
            'start_date': start_date.isoformat() if start_date else 'all time',
            'end_date': now.isoformat(),
            'total_income': total_income,
            'total_expense': total_expense,
            'profit': total_income - total_expense,
            'summary': [dict(r) for r in summary],
            'transactions': [dict(r) for r in transactions]
        }
    finally:
        await conn.close()
