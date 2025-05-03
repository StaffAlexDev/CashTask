from json import load

from aiogram.fsm.state import State, StatesGroup

from database.db_settings import get_db_connection
from config.constants import LANGUAGE_DIR
from utils.enums import Role


class OrderStates(StatesGroup):
    waiting_for_client = State()  # Ожидаем клиента
    waiting_for_car = State()  # Ожидание выбора автомобиля
    waiting_for_service = State()  # Ожидание выбора услуги
    waiting_for_employer = State()  # Кто будет выполнять работу
    waiting_for_order_confirmation = State()  # Ожидание подтверждения


class ClientStates(StatesGroup):
    new_client_data = State()
    new_car_data = State()


class FinanceStates(StatesGroup):
    investments = State()
    from_the_car = State()
    waiting_for_photo = State()


class EmployerState(StatesGroup):
    waiting_new_car = State()
    new_data_for_car = State()


class UserCookies:
    _lang_cache = {}

    def __init__(self, telegram_id):
        self.telegram_id = telegram_id
        self.lang = "ru"
        self.role = None

    def get_lang(self):
        try:
            if self.lang not in self._lang_cache:
                with open(f"{LANGUAGE_DIR}/{self.lang}.json", encoding="utf-8") as lang_file:
                    self._lang_cache[self.lang] = load(lang_file)
            return self._lang_cache[self.lang]
        except Exception as e:
            print(f"Ошибка при загрузке языкового файла: {e}")
            return {}

    def get_role(self) -> Role:
        if self.role is None:
            try:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT role FROM employees WHERE telegram_id = ?
                    ''', (self.telegram_id,))
                    result = cursor.fetchone()
                    if result:
                        self.role = result[0]
                    else:
                        self.role = Role.WORKER.value
            except Exception as e:
                print(f"Ошибка при получении роли из базы: {e}")
                self.role = Role.WORKER.value
        return Role(self.role)

    def update_profile(self, lang=None, role=None):
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                if lang is not None:
                    self.lang = lang
                    cursor.execute('''
                        UPDATE employees SET lang = ?
                        WHERE telegram_id = ?
                    ''', (lang, self.telegram_id))
                if role is not None:
                    self.role = role
                    cursor.execute('''
                        UPDATE employees SET role = ?
                        WHERE telegram_id = ?
                    ''', (role, self.telegram_id))
                cursor.execute('''
                    INSERT OR IGNORE INTO employees (telegram_id, lang, role)
                    VALUES (?, ?, ?)
                ''', (self.telegram_id, self.lang, self.role))
                conn.commit()
        except Exception as e:
            print(f"Ошибка при обновлении профиля: {e}")
