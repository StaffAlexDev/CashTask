from .formatting import LocalizedString
from .lang_base import *

lang = LangBase(
    greetings=Greetings(
        unknown_user="You are not registered",
        waiting_accept="Please wait for approval",
        welcome="Welcome!"
    ),

    language=Language(
        select_lang="Select a language",
        accept_lang="Language saved"
    ),

    roles=Roles(
        worker="Worker",
        admin="Admin",
        supervisor="Supervisor",
        superadmin="Super Admin"
    ),

    # Статусы заявок
    statuses=Statuses(
        new="New",
        in_progress="In progress",
        done="Completed"
    ),

    # Сообщения по шагам заказа
    orders=Orders(
        order_types="Select order type",
        phone_client="Enter client's phone number"
    ),

    # Сообщения по шагам задач
    tasks=Tasks(
        task_action="Select action"
    ),

    finances=Finances(
        income="Income",
        expense="Expense",
        fuel="Fuel"
    ),

    periods=Periods(
        day="Day",
        week="Week",
        two_weeks="Two weeks",
        month="Month",
        all="All time"
    ),

    ui_buttons=UiButtons(
        # Главные действия по ролям
        car_in_work="Car in work",
        materials="Materials needed",
        tasks="Tasks",
        new_order="New work order",
        order_in_work="Work order in progress",
        add_task="Add task",
        what_buy="What to buy",
        reports="Reports",

        # Финансы
        finance_income="Income",
        finance_expense="Expense",
        finance_fuel="Fuel",
        finance_report="Expense report",

        # Навигация и управление
        back="Back",
        main_menu="Main menu",
        cancel="Cancel",
        close="Close",
        submit="Save",
        confirm="Confirm",
        access_accept="Accept",
        access_reject="Reject",

        # Пагинация
        prev_page="⏮ Back",
        next_page="Next ⏭",
        exit_pagination="🚫 Close list",
        back_to_list="🔙 Back to list",

        # Клиенты и авто
        add_client="➕ Add client",
        all_clients="👥 Clients list",
        add_car="➕ Add car",
        all_cars="🚗 All cars",
        my_park_add="Add my car",
        my_park_list="My cars",

        # Отчёты по периодам
        period_day="Day",
        period_week="Week",
        period_two_weeks="Two weeks",
        period_month="Month",

        # Заказы
        open_orders="Open orders",
        completed_orders="Completed orders",

        # Действия с машинами сотрудников
        plate="License plate",
        inspection="Inspection",
        insurance="Insurance",
        edit="✏️ Edit",
        delete="🗑 Delete",
        restore="♻️ Restore",

        # Разделение списков
        by_client="By client",
        by_car="By car",
        from_car="From car",
        general="General"
    ),

    info=Info(
        new_user_info_notif=LocalizedString(
            "User {name} requires confirmation of the position: {position}"
        ),
        user_accept="User confirmed",
        user_accept_confirm="Your request has been approved",
        no_access="You do not have access!",
        unknown_action="Unknown action"
    )
)
