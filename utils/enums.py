import re
from enum import Enum
from typing import TypeVar, Type, List

T = TypeVar("T", bound="BaseEnum")


class BaseEnum(str, Enum):
    """
    Базовый Enum для проекта с поддержкой:
    - ordered() → все элементы
    - all_except() → все элементы кроме указанных
    - values() → список строковых значений
    - for_ui() → элементы для UI (исключает те, что не должны показываться)
    - display_name() → локализованное название
    """

    @classmethod
    def ordered(cls: Type[T]) -> List[T]:
        return list(cls)

    @classmethod
    def all_except(cls, *excluded) -> List["BaseEnum"]:
        return [item for item in cls.ordered() if item not in excluded]

    @classmethod
    def values(cls: Type[T]) -> List[str]:
        return [item.value for item in cls]

    @classmethod
    def exclude_from_ui(cls) -> List["BaseEnum"]:
        return []

    @classmethod
    def for_ui(cls):
        return [item for item in cls if item not in cls.exclude_from_ui()]

    @classmethod
    def lang_section(cls) -> str:
        """
        Возвращает название секции для перевода в snake_case + "s" в конце
        Например:
            Role -> roles
            OrderStatus -> order_statuses
        """
        name = cls.__name__
        # Преобразовать CamelCase в snake_case
        snake = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
        return snake + "s"

    def display_name(self, lang_data: object) -> str:
        section = getattr(lang_data, self.lang_section(), None)

        if section is None:
            return str(self.value)

        return getattr(section, self.value, self.value)


class Role(BaseEnum):
    UNKNOWN = "unknown"
    WORKER = "worker"
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    SUPERADMIN = "superadmin"

    @classmethod
    def exclude_from_ui(cls):
        return [cls.UNKNOWN, cls.SUPERADMIN]

    @classmethod
    def get_upper_roles(cls, role) -> list:
        """Получить все роли выше данной"""
        roles = cls.ordered()
        index = roles.index(role)
        return roles[index + 1:]


class OrderStatus(BaseEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskStatus(BaseEnum):
    IN_PROGRESS = "in_progress"
    DONE = "done"


class FinanceType(BaseEnum):
    INCOME = "income"
    EXPENSE = "expense"
    FUEL = "fuel"


class Period(BaseEnum):
    DAY = "day"
    WEEK = "week"
    TWO_WEEKS = "two_weeks"
    MONTH = "month"
    ALL = "all"
