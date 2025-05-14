from aiogram.fsm.state import State, StatesGroup
from database.settings_pg import get_db_connection
from utils.enums import Role


class OrderStates(StatesGroup):
    waiting_for_client = State()
    waiting_for_car = State()
    waiting_for_service = State()
    waiting_for_employer = State()
    waiting_for_order_confirmation = State()


class ClientStates(StatesGroup):
    new_client_data = State()
    new_car_data = State()


class FinanceStates(StatesGroup):
    investments = State()
    from_the_car = State()
    waiting_for_photo = State()


class EmployerState(StatesGroup):
    waiting_add_car = State()
    waiting_update_car = State()


class UserContext:
    """
    Контекст пользователя. Загружает из базы:
    - telegram_id
    - language
    - role
    - company_id
    """
    def __init__(self, telegram_id: int):
        self.telegram_id = telegram_id
        self.lang_code = "ru"
        self.role = Role.UNKNOWN.value
        self.company_id = None

    async def load_from_db(self):
        conn = await get_db_connection()
        try:
            row = await conn.fetchrow(
                '''
                SELECT language, role, company_id
                  FROM employees
                 WHERE telegram_id = $1
                ''',
                self.telegram_id
            )
            if row:
                if row['language']:
                    self.lang_code = row['language']
                if row['role']:
                    self.role = row['role']
                self.company_id = row['company_id']
        finally:
            await conn.close()

    @property
    def lang(self):
        from languages.loader import get_lang
        return get_lang(self.lang_code)

    def get_role(self) -> Role:
        return Role(self.role)

    async def update_lang(self, lang_code: str):
        conn = await get_db_connection()
        try:
            await conn.execute(
                '''
                UPDATE employees
                   SET language = $1
                 WHERE telegram_id = $2
                ''',
                lang_code, self.telegram_id
            )
            self.lang_code = lang_code
        finally:
            await conn.close()
