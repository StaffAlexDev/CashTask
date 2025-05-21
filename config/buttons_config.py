from functools import partial

from database.clients_pg import get_all_clients, get_all_cars
from database.employees_pg import get_all_employees
from database.orders_pg import get_all_orders
from database.tasks_pg import get_all_tasks
from utils.enums import Role
from languages.ru import lang as ru_lang
from languages.en import lang as en_lang

BUTTONS_COMMON = {
    "start_menu": {
        "base": ["company_crate", "company_join"]
    },
    # Главное меню по ролям
    "main_menu": {
        Role.WORKER.value: ["order_in_work", "materials"],
        Role.ADMIN.value: ["car_in_work", "materials", "new_order", "add_task", "what_buy", "tasks", "get_my_company"],
        Role.SUPERVISOR.value: ["car_in_work", "materials", "new_order",
                                "add_task", "what_buy", "tasks", "get_my_company"],

        Role.SUPERADMIN.value: ["car_in_work", "materials", "new_order",
                                "add_task", "what_buy", "tasks", "get_my_company"]
    },

    # Финансы
    "finance": {
        "base": ["finance_income", "finance_expense", "finance_fuel"],
        Role.SUPERADMIN.value: ["finance_report"]
    },

    # Заказы
    "orders": {
        "base": ["new_order", "open_orders"],
        Role.SUPERADMIN.value: ["completed_orders"]
    },

    # Навигация
    "navigation": ["back", "main_menu", "cancel", "close"],
    # "submit", "confirm",
    # Управление
    "control": ["access_accept", "access_reject"],

    # Пагинация
    "pagination": ["prev_page", "next_page", "exit_pagination", "back_to_list"],

    # Клиенты
    "clients": ["add_client", "all_clients"],

    # Автомобили
    "cars": ["add_car", "all_cars", "my_park_add", "my_park_list"],

    # Отчеты
    "reports": ["period_day", "period_week", "period_two_weeks", "period_month"],

    # Типы заказов
    "order_types": ["by_client", "by_car"],

    # Типы финансов
    "finance_types": ["from_car", "general"],

    # Действия с авто
    "car_actions": ["plate", "inspection", "insurance", "edit", "delete", "restore"]
}

LANGUAGE_REGISTRY = {
    "ru": ("Русский", ru_lang),
    "en": ("English", en_lang)
}

# =================================================================================================

pagination_configs = {
    "client": {
        "get_items_func": get_all_clients,
        "build_button_text": lambda c: f"{c['first_name']} {c['last_name']} – ☎ {c['phone_number']}",
        "back_callback": "clients_menu",
        "title": "Список клиентов",
        "filters": {}
    },
    "car": {
        "get_items_func": get_all_cars,
        "build_button_text": lambda c: f"{c['car_brand']} {c['car_model']} – {c['license_plate']}",
        "back_callback": "cars_menu",
        "title": "Список автомобилей",
        "filters": {}
    },
    "order": {
        "get_items_func": partial(get_all_orders, status="in_progress"),
        "build_button_text": lambda o: f"Заказ #{o['order_id']} – {o['description']} ({o['status']})",
        "back_callback": "orders_menu",
        "title": "Список заказов",
        "filters": {}
    },
    "task": {
        "get_items_func": get_all_tasks,
        "build_button_text": lambda t: f"Задача #{t['task_id']} – {t['description']} ({t['status']})",
        "back_callback": "tasks_menu",
        "title": "Список задач",
        "filters": {"assigned_to": None}
    },
    "employee": {
        "get_items_func": get_all_employees,
        "build_button_text": lambda e: f"{e['first_name']} {e['last_name']} – роль: {e['role']}",
        "back_callback": "employees_menu",
        "title": "Список сотрудников",
        "filters": {"role": "worker"}
    }
}
