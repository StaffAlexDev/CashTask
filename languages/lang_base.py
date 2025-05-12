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
class Statuses:
    new: str = ""
    in_progress: str = ""
    done: str = ""


# @dataclass
# class Clients:
#     pass


@dataclass
class Employers:
    get_new_car: str = ""


@dataclass
class Orders:
    order_types: str = ""
    phone_client: str = ""


@dataclass
class Tasks:
    task_action: str = ""


@dataclass
class Finances:
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
    # Главные действия по ролям
    car_in_work: str = ""
    materials: str = ""
    tasks: str = ""
    new_order: str = ""
    order_in_work: str = ""
    add_task: str = ""
    what_buy: str = ""
    reports: str = ""

    # Финансы
    finance_income: str = ""
    finance_expense: str = ""
    finance_fuel: str = ""
    finance_report: str = ""

    # Навигация и управление
    back: str = ""
    main_menu: str = ""
    cancel: str = ""
    close: str = ""
    submit: str = ""
    confirm: str = ""
    access_accept: str = ""
    access_reject: str = ""

    # Пагинация
    prev_page: str = ""
    next_page: str = ""
    exit_pagination: str = ""
    back_to_list: str = ""

    # Клиенты и авто
    add_client: str = ""
    all_clients: str = ""
    add_car: str = ""
    all_cars: str = ""
    my_park_add: str = ""
    my_park_list: str = ""

    # Отчёты по периодам
    period_day: str = ""
    period_week: str = ""
    period_two_weeks: str = ""
    period_month: str = ""

    # Заказы
    open_orders: str = ""
    completed_orders: str = ""

    # Действия с машинами сотрудников
    plate: str = ""
    inspection: str = ""
    insurance: str = ""
    edit: str = ""
    delete: str = ""
    restore: str = ""
    by_client: str = "",
    by_car: str = "",
    from_car: str = "",
    general: str = "",


@dataclass
class Info:
    """
       Информационные сообщения.

       new_user_info_notif: Пользователь {name}, требует подтверждения должности: {position}
       """
    new_user_info_notif: str = ""
    user_accept: str = ""
    user_accept_confirm: str = ""
    no_access: str = ""
    unknown_action: str = ""
    user_rejected: str = ""
    your_been_rejected: str = ""


@dataclass
class Err:  # Errors
    no_user_data: str = ""


@dataclass
class LangBase:
    greetings: Greetings
    language: Language
    roles: Roles
    statuses: Statuses
    employers: Employers
    orders: Orders
    tasks: Tasks
    finances: Finances
    periods: Periods
    ui_buttons: UiButtons
    info: Info
    err: Err


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

