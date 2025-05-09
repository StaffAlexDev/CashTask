from hlam.db.employees import get_all_employees
from hlam.db.clients import get_all_cars, get_all_clients
from hlam.db.tasks import get_all_tasks
from hlam.db.orders import get_all_orders
from utils.enums import Role

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
# -------------------------------------------------------------------------------------------------
UI_BUTTONS = {  # Пробное дублирование BUTTONS
    "car_in_work": "car_in_work",
    "materials": "materials",
    "tasks": "tasks",
    "new_order": "new_order",
    "order_in_work": "order_in_work",
    "add_task": "add_task",
    "what_buy": "what_buy",
    "reports": "reports"
}

BUTTONS_FOR_ROLE = {
    Role.WORKER.value: ["order_in_work", "materials"],
    Role.ADMIN.value: ["car_in_work", "materials", "new_order", "add_task", "what_buy", "income_expense", "tasks"],
    Role.SUPERADMIN.value: ["car_in_work", "what_buy", "income_expense", "reports"]
    }


SUPPORTED_LANGUAGES = {
    "ru": "Русский",
    "en": "English",
}
# =================================================================================================
pagination_configs = {
    "client": {
        "get_items_func": lambda **kwargs: get_all_clients(),
        "build_button_text": lambda c: f"{c['first_name']} {c['last_name']} – ☎ {c['phone_number']}",
        "back_callback": "clients_menu",
        "title": "Список клиентов",
        "filters": None
    },
    "car": {
        "get_items_func": lambda **kwargs: get_all_cars(),
        "build_button_text": lambda c: f"{c['car_brand']} {c['car_model']} – {c['license_plate']}",
        "back_callback": "cars_menu",
        "title": "Список автомобилей",
        "filters": None
    },
    "order": {
        "get_items_func": lambda status=None, **kwargs: get_all_orders(status),
        "build_button_text": lambda o: f"Заказ #{o['order_id']} – {o['description']} ({o['status']})",
        "back_callback": "orders_menu",
        "title": "Список заказов",
        "filters": {"status": "in_progress"}
    },
    "task": {
        "get_items_func": lambda assigned_to=None, **kwargs: get_all_tasks(assigned_to),
        "build_button_text": lambda t: f"Задача #{t['task_id']} – {t['description']} ({t['status']})",
        "back_callback": "tasks_menu",
        "title": "Список задач",
        "filters": {"assigned_to": None}
    },
    "employee": {
        "get_items_func": lambda role=None, **kwargs: get_all_employees(role),
        "build_button_text": lambda e: f"{e['first_name']} {e['last_name']} – роль: {e['role']}",
        "back_callback": "employees_menu",
        "title": "Список сотрудников",
        "filters": {"role": "worker"}
    }
}

