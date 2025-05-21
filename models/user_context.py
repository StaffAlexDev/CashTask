from typing import List, Tuple, Callable, Any

from database.settings_pg import get_db_connection
from utils.enums import Role


class UserContext:
    """
    Контекст пользователя. Загружает из базы:
    - telegram_id
    - language
    - role
    - company_id
    - nav_stack - хранит шаги действий для навигации
    """
    def __init__(self, telegram_id: int):
        self.telegram_id = telegram_id
        self.lang_code = "ru"
        self.role = Role.UNKNOWN
        self.company_id = None
        self.nav_stack: List[Tuple[Callable[..., Any], tuple, dict]] = []

    def push_nav(self, handler: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """Добавить в стек экран (функцию-рендер) вместе с её аргументами."""
        self.nav_stack.append((handler, args, kwargs))

    def pop_nav(self) -> Tuple[Callable[..., Any], tuple, dict] | None:
        """
        Снять текущий экран и вернуть предыдущий.
        Возвращает None, если стека нет или в нём < 2 элементов.
        """
        if len(self.nav_stack) < 2:
            return None
        self.nav_stack.pop()  # убираем текущий
        return self.nav_stack[-1]

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
                    self.role = Role(row['role'])
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
