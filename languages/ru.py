from .formatting import LocalizedString
from .lang_base import *

lang = LangBase(
    greetings=Greetings(
        unknown_user="Вы не зарегистрированы",
        waiting_accept="Ожидайте подтверждения",
        welcome="Добро пожаловать!"
    ),

    language=Language(
        select_lang="Выберите язык",
        accept_lang="Язык сохранён"
    ),

    roles=Roles(
        worker="Рабочий",
        admin="Админ",
        supervisor="Супервайзер",
        superadmin="Суперадмин"
    ),

    order_statuses=OrderStatuses(
        new="Новый",
        in_progress="В работе",
        done="Завершён"
    ),

    task_statuses=TaskStatuses(
        in_progress="В работе",
        done="Завершено"
    ),

    finance_types=FinanceTypes(
        income="Доход",
        expense="Расход",
        fuel="Топливо"
    ),

    periods=Periods(
        day="День",
        week="Неделя",
        two_weeks="Две недели",
        month="Месяц",
        all="За всё время"
    ),

    ui_buttons=UiButtons(
        car_in_work="Авто в работе",
        materials="Нужны материалы",
        tasks="Задачи",
        new_order="Новый заказ-наряд",
        order_in_work="Заказ-наряд в работе",
        add_task="Добавить задачу",
        what_buy="Что купить",
        reports="Отчёты"
    ),

    info=Info(
        new_user_info_notif=LocalizedString("Пользователь {name}, требует подтверждения должности: {position}"),
        user_accept="Пользователь подтвержден"
    )
)
