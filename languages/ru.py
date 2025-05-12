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

    statuses=Statuses(
        new="Новый",
        in_progress="В работе",
        done="Завершён"
    ),
    employers=Employers(
        get_new_car="Запиши через запятую данные машины:\n"
                    "(марка, модель, номерной знак, дата окончания тех. осмотра(день.месяц.год), "
                    "дата окончания страховки(день.месяц.год)):"
    ),
    orders=Orders(
        order_types="Выберите тип заказа",
        phone_client="Введи номер телефона клиента"
    ),

    tasks=Tasks(
        task_action="Выберите действие"
    ),

    finances=Finances(
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
        # Главные действия по ролям
        car_in_work="Авто в работе",
        materials="Нужны материалы",
        tasks="Задачи",
        new_order="Новый заказ-наряд",
        order_in_work="Заказ-наряд в работе",
        add_task="Добавить задачу",
        what_buy="Что купить",
        reports="Отчёты",

        # Финансы
        finance_income="Доход",
        finance_expense="Расход",
        finance_fuel="Топливо",
        finance_report="Отчёт по расходам",

        # Навигация и управление
        back="Назад",
        main_menu="Главное меню",
        cancel="Отмена",
        close="Закрыть",
        submit="Сохранить",
        confirm="Подтвердить",
        access_accept="Принять",
        access_reject="Отклонить",

        # Пагинация
        prev_page="⏮ Назад",
        next_page="Вперёд ⏭",
        exit_pagination="🚫 Закрыть список",
        back_to_list="🔙 Назад к списку",

        # Клиенты и авто
        add_client="➕ Добавить клиента",
        all_clients="👥 Список клиентов",
        add_car="➕ Добавить авто",
        all_cars="🚗 Все авто",
        my_park_add="Добавить свою машину",
        my_park_list="Мои машины",

        # Отчёты по периодам
        period_day="За день",
        period_week="За неделю",
        period_two_weeks="За 2 недели",
        period_month="За месяц",

        # Заказы
        open_orders="Открытые заказы",
        completed_orders="Завершённые заказы",

        # Действия с машинами сотрудников
        plate="Номер",
        inspection="Техосмотр",
        insurance="Страховка",
        edit="✏️ Изменить",
        delete="🗑 Удалить",
        restore="♻️ Восстановить",
        by_client="По клиенту",
        by_car="По машине",
        from_car="От машины",
        general="Общий",
    ),

    info=Info(
        new_user_info_notif=LocalizedString("Пользователь {name}, требует подтверждения должности: {position}"),
        user_accept="Пользователь подтвержден",
        user_accept_confirm="Ваша заявка принята",
        no_access="У вас нет доступа!",
        unknown_action="Это неизвестное действие",
        user_rejected="Пользователь отклонён!",
        your_been_rejected="Ваша заявка отклонена!"
    ),
    err=Err(
        no_user_data="Ошибка: нет данных о пользователе."
    )
)
