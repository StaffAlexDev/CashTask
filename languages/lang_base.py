from dataclasses import dataclass


@dataclass
class Greetings:
    unknown_user: str = ""
    waiting_accept: str = ""
    welcome: str = ""


@dataclass
class Language:
    select_lang: str = ""
    accept_lang: str = ""


@dataclass
class Roles:
    worker: str = ""
    admin: str = ""
    supervisor: str = ""
    superadmin: str = ""


@dataclass
class OrderStatuses:
    new: str = ""
    in_progress: str = ""
    done: str = ""


@dataclass
class TaskStatuses:
    in_progress: str = ""
    done: str = ""


@dataclass
class FinanceTypes:
    income: str = ""
    expense: str = ""
    fuel: str = ""


@dataclass
class Periods:
    day: str = ""
    week: str = ""
    two_weeks: str = ""
    month: str = ""
    all: str = ""


@dataclass
class UiButtons:
    car_in_work: str = ""
    materials: str = ""
    tasks: str = ""
    new_order: str = ""
    order_in_work: str = ""
    add_task: str = ""
    what_buy: str = ""
    reports: str = ""


@dataclass
class Info:
    """
       Информационные сообщения.

       new_user_info_notif: Пользователь {name}, требует подтверждения должности: {position}
       """
    new_user_info_notif: str = ""
    user_accept: str = ""


@dataclass
class LangBase:
    greetings: Greetings
    language: Language
    roles: Roles
    order_statuses: OrderStatuses
    task_statuses: TaskStatuses
    finance_types: FinanceTypes
    periods: Periods
    ui_buttons: UiButtons
    info: Info


if __name__ == "__main__":
    print("Greetings".lower())
    print("Language".lower())
    print("Roles".lower())
    print("OrderStatuses".lower())
    print("TaskStatuses".lower())
    print("FinanceTypes".lower())
    print("Periods".lower())
    print("UiButtons".lower())
    print("Info".lower())

