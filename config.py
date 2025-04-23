import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
PHOTOS_DIR = BASE_DIR / "receipts"
LANGUAGE_DIR = BASE_DIR / "languages"
DB_PATH = BASE_DIR / "database/cash_task.db"

USER_ROLES = ['worker', 'admin', 'superadmin']
COUNT_DAYS = {1, 2, 7, 14}

# Patterns
INVOICE_PATTERN = re.compile(r"(-?\d{1,5})\s+(расход|приход)\s*,?\s*(.+)", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"^\+?\d{10,15}$", re.IGNORECASE)
BRAND_PATTERN = r"^[A-Za-zА-Яа-яЁё]+$"
MODEL_PATTERN = r"^[A-Za-zА-Яа-яЁё0-9\- ]+$"
DATE_PATTERN = r"^\d{2}\.\d{2}\.\d{4}$"

# List Buttons
BUTTONS = {
        "car_in_work": {"text": "Авто в работе", "callback_data": "car_in_work"},
        "materials": {"text": "Нужны материалы", "callback_data": "materials"},
        "tasks": {"text": "Задачи", "callback_data": "tasks"},
        "new_order": {"text": "Заказ-Наряд", "callback_data": "new_order"},
        "order_in_work": {"text": "Заказ-Наряд", "callback_data": "order_in_work"},
        "add_task": {"text": "Добавить задачу", "callback_data": "add_task"},
        "what_buy": {"text": "Что купить", "callback_data": "what_buy"},
        "reports": {"text": "Отчеты", "callback_data": "reports"}
    }

BUTTONS_FOR_ROLE = {
    "worker": ["order_in_work", "materials"],
    "admin": ["car_in_work", "materials", "new_order", "add_task", "what_buy", "income_expense", "tasks"],
    "superadmin": ["car_in_work", "what_buy", "income_expense", "reports"]
    }

PERIOD_BUTTONS = {
        "day": {"text": "День", "callback_data": "day"},
        "week": {"text": "Неделя", "callback_data": "week"},
        "two_weeks": {"text": "Две недели", "callback_data": "two_weeks"},
        "month": {"text": "Месяц", "callback_data": "month"},
        "all": {"text": "За все время", "callback_data": "all"},
    }  # При изменении тут нужно и в функции -> get_financial_report -> period_map


if __name__ == '__main__':
    print("count_days".upper())
