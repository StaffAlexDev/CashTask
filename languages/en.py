from .formatting import LocalizedString
from .lang_base import *

lang = LangBase(
    greetings=Greetings(
        unknown_user="Hello, you are not registered yet",
        unknown_company="Select an action: create a new company or join an existing one",
        waiting_accept="Please wait for approval",
        welcome="Welcome!"
    ),

    language=Language(
        select_lang="Choose a language",
        accept_lang="Language saved"
    ),

    roles=Roles(
        worker="Worker",
        admin="Admin",
        supervisor="Supervisor",
        superadmin="Superadmin"
    ),

    statuses=Statuses(
        new="New",
        in_progress="In Progress",
        done="Completed"
    ),

    employers=Employers(
        get_new_car="Enter car data separated by commas:\n"
                    "(brand, model, license plate, technical inspection expiry date (DD.MM.YYYY), "
                    "insurance expiry date (DD.MM.YYYY)):"
    ),

    orders=Orders(
        order_types="Select order type",
        phone_client="Enter client's phone number"
    ),

    tasks=Tasks(
        task_action="Select an action"
    ),

    finances=Finances(
        income="Income",
        expense="Expense",
        fuel="Fuel"
    ),

    periods=Periods(
        day="Day",
        week="Week",
        two_weeks="Two Weeks",
        month="Month",
        all="All Time"
    ),

    ui_buttons=UiButtons(
        # Start menu
        company_crate="Create",
        company_join="Join",

        # Main actions by roles
        car_in_work="Cars in Work",
        materials="Materials Needed",
        tasks="Tasks",
        new_order="New Work Order",
        order_in_work="Work Orders in Progress",
        add_task="Add Task",
        what_buy="What to Buy",
        reports="Reports",

        # Finances
        finance_income="Income",
        finance_expense="Expense",
        finance_fuel="Fuel",
        finance_report="Financial Report",

        # Navigation and control
        back="Back",
        main_menu="Main Menu",
        cancel="Cancel",
        close="Close",
        submit="Save",
        confirm="Confirm",
        access_accept="Accept",
        access_reject="Reject",

        # Pagination
        prev_page="⏮ Previous",
        next_page="Next ⏭",
        exit_pagination="🚫 Close List",
        back_to_list="🔙 Back to List",

        # Clients and cars
        add_client="➕ Add Client",
        all_clients="👥 Client List",
        add_car="➕ Add Car",
        all_cars="🚗 All Cars",
        my_park_add="Add My Car",
        my_park_list="My Cars",

        # Period reports
        period_day="For a Day",
        period_week="For a Week",
        period_two_weeks="For 2 Weeks",
        period_month="For a Month",

        # Orders
        open_orders="Open Orders",
        completed_orders="Completed Orders",

        # Employee car actions
        plate="Plate",
        inspection="Inspection",
        insurance="Insurance",
        edit="✏️ Edit",
        delete="🗑 Delete",
        restore="♻️ Restore",
        by_client="By Client",
        by_car="By Car",
        from_car="From Car",
        general="General",
    ),

    info=Info(
        new_user_info_notif=LocalizedString("User {name} requests approval for position: {position}"),
        user_accept="User approved",
        user_accept_confirm="Your request has been approved",
        no_access="You do not have access!",
        unknown_action="Unknown action",
        user_rejected="User rejected!",
        your_been_rejected="Your request has been rejected!"
    ),

    err=Err(
        no_user_data="Error: no user data."
    )
)
