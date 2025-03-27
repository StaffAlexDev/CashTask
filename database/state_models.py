from json import load

from aiogram.fsm.state import State, StatesGroup

from database.db_settings import get_db_connection


class OrderStates(StatesGroup):
    waiting_for_car = State()  # Ожидание выбора автомобиля
    waiting_for_service = State()  # Ожидание выбора услуги
    waiting_for_confirmation = State()  # Ожидание подтверждения


class UserRegistrationObject(StatesGroup):
    waiting_for_confirmation = State()


class FinanceStates(StatesGroup):
    investments = State()
    from_the_car = State()


class UserCookies:
    _lang_cache = {}

    def __init__(self, telegram_id):
        self.telegram_id = telegram_id
        self.lang = "ru"
        self.role = None

    def set_lang(self, lang):
        self.lang = lang
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO users (telegram_id, lang)
                    VALUES (?, ?)
                ''', (self.telegram_id, self.lang))
                conn.commit()
        except Exception as e:
            print(f"Ошибка при обновлении языка: {e}")

    def get_lang(self):
        try:
            if self.lang not in self._lang_cache:
                with open(f"languages/{self.lang}.json", encoding="utf-8") as lang_file:
                    self._lang_cache[self.lang] = load(lang_file)
            return self._lang_cache[self.lang]
        except Exception as e:
            print(f"Ошибка при загрузке языкового файла: {e}")
            return {}

    def get_role(self):
        # Ленивая загрузка роли: если роль не загружена, загружаем её из базы
        if self.role is None:
            try:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT role FROM users WHERE telegram_id = ?
                    ''', (self.telegram_id,))
                    result = cursor.fetchone()
                    if result:
                        self.role = result[0]
                    else:
                        self.role = "user"  # Роль по умолчанию, если её нет в базе
            except Exception as e:
                print(f"Ошибка при получении роли из базы: {e}")
                self.role = "user"  # Роль по умолчанию в случае ошибки
        return self.role

    def set_role(self, role):
        # Обновляем роль в ОЗУ и в базе данных
        self.role = role
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO users (telegram_id, role)
                    VALUES (?, ?)
                ''', (self.telegram_id, self.role))
                conn.commit()
        except Exception as e:
            print(f"Ошибка при обновлении роли: {e}")
