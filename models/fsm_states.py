from aiogram.fsm.state import State, StatesGroup


class StartState(StatesGroup):
    waiting_company_name = State()
    waiting_invite_code = State()


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


class HelpState(StatesGroup):
    waiting_for_text = State()
