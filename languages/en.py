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

    order_statuses=OrderStatuses(
        new="New",
        in_progress="In progress",
        done="Completed"
    ),

    task_statuses=TaskStatuses(
        in_progress="In progress",
        done="Completed"
    ),

    finance_types=FinanceTypes(
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
        car_in_work="Car in work",
        materials="Materials needed",
        tasks="Tasks",
        new_order="New work order",
        order_in_work="Work order in progress",
        add_task="Add task",
        what_buy="What to buy",
        reports="Reports"
    ),

    info=Info(
        new_user_info_notif=LocalizedString("User {name} requires confirmation of the position: {position}"),
        user_accept="User confirmed"
    )
)
