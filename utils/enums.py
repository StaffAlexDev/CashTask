from enum import Enum
from typing import TypeVar, Type, List

T = TypeVar("T", bound="BaseEnum")


class BaseEnum(str, Enum):
    @classmethod
    def ordered(cls: Type[T]) -> List[T]:
        return list(cls)

    @classmethod
    def all_except(cls, *excluded) -> List[str]:
        return [item.value for item in cls.ordered() if item not in excluded]

    @classmethod
    def values(cls: Type[T]) -> List[str]:
        return [item.value for item in cls]

    def display_name(self, lang_data: dict) -> str:
        """Локализованное отображение"""
        section = lang_data.get(self.__class__.__name__.lower() + "s", {})
        return section.get(self.value, self.value)


class Role(BaseEnum):
    WORKER = "worker"
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    REGIONAL_ADMIN = "regional_admin"
    SUPERADMIN = "superadmin"

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
