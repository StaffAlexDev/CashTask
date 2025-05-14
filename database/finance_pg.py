from database.settings_pg import get_db_connection
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


async def add_finance(
    company_id: int,
    amount: float,
    direction: str,
    category: str,
    admin_id: int,
    client_id: int = None,
    car_id: int = None,
    advance_src: int = None,
    description: str = None,
    photo: str = None
) -> None:
    """
    Создать запись о финансовой операции в единой таблице finances.
    direction: 'in' или 'out'
    category: 'director_fund','client_advance','part_purchase','supplies', и т.д.
    advance_src: ссылка на исходный аванс (finance_id) при расходе из аванса клиента
    """
    conn = await get_db_connection()
    try:
        await conn.execute(
            '''
            INSERT INTO finances (
                amount, direction, category,
                company_id, admin_id, client_id, car_id, advance_src,
                description, photo
            ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
            ''',
            amount, direction, category,
            company_id, admin_id, client_id, car_id, advance_src,
            description, photo
        )
    finally:
        await conn.close()


async def get_finances_by_order(
    company_id: int,
    order_id: int
) -> list[dict]:
    """
    Вернуть все финансовые записи, связанные с конкретным заказом (часто category='part_purchase').
    """
    conn = await get_db_connection()
    try:
        rows = await conn.fetch(
            '''
            SELECT * FROM finances
            WHERE company_id = $1
              AND car_id = (
                  SELECT car_id FROM orders WHERE order_id = $2 AND company_id = $1
              )
              AND category = 'part_purchase'
            ORDER BY created_at DESC
            ''',
            company_id, order_id
        )
        return [dict(r) for r in rows]
    finally:
        await conn.close()


async def get_financial_report(
    company_id: int,
    period: str = 'all'
) -> dict:
    """
    Сводный отчёт по операциям за период:
    - total_income, total_expense, profit
    - breakdown по категориям
    - список последних транзакций
    """
    now = datetime.now()
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

    # Условия и параметры
    cond = 'company_id = $1' + (" AND created_at >= $2" if start_date else "")
    params = [company_id]
    if start_date:
        params.append(start_date)

    conn = await get_db_connection()
    try:
        # Суммы по направлениям
        summary_q = f'''
            SELECT direction, SUM(amount) AS total, COUNT(*) AS count
            FROM finances
            WHERE {cond}
            GROUP BY direction
        '''
        summary = await conn.fetch(summary_q, *params)

        # Свод по категориям
        by_cat_q = f'''
            SELECT category, direction, SUM(amount) AS total
            FROM finances
            WHERE {cond}
            GROUP BY category, direction
        '''
        by_cat = await conn.fetch(by_cat_q, *params)

        # Последние транзакции
        tx_q = f'''
            SELECT * FROM finances
            WHERE {cond}
            ORDER BY created_at DESC
            LIMIT 100
        '''
        transactions = await conn.fetch(tx_q, *params)

        total_income = sum(r['total'] for r in summary if r['direction'] == 'in')
        total_expense = sum(r['total'] for r in summary if r['direction'] == 'out')

        return {
            'period': period,
            'start_date': start_date.isoformat() if start_date else 'all time',
            'end_date': now.isoformat(),
            'total_income': total_income,
            'total_expense': total_expense,
            'profit': total_income - total_expense,
            'summary': [dict(r) for r in summary],
            'by_category': [dict(r) for r in by_cat],
            'transactions': [dict(r) for r in transactions]
        }
    finally:
        await conn.close()
