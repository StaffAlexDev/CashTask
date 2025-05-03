from datetime import datetime

from config.patterns import COUNT_DAYS
from database.db_crud import get_employees_cars
from settings import bot


async def checking_the_end_date_of_documents():
    employer_cars = get_employees_cars()
    today = datetime.today()
    notifications = {}

    for car in employer_cars:
        technical_inspection = car.get("technical_inspection")
        insurance = car.get("insurance")
        technical_inspection_date = datetime.strptime(technical_inspection, "%d.%m.%Y")
        insurance_date = datetime.strptime(insurance, "%d.%m.%Y")

        technical_inspection_days_left = (technical_inspection_date - today).days
        insurance_days_left = (insurance_date - today).days

        employer_id = car.get("employer_id")

        # Обработаем страховку
        if insurance_days_left in COUNT_DAYS:
            if employer_id not in notifications:
                notifications[employer_id] = []
            notifications[employer_id].append({
                "type": "страховка",
                "days_left": insurance_days_left
            })

        # Обработаем техосмотр
        if technical_inspection_days_left in COUNT_DAYS:
            if employer_id not in notifications:
                notifications[employer_id] = []
            notifications[employer_id].append({
                "type": "техосмотр",
                "days_left": technical_inspection_days_left
            })

    # Отправляем уведомления и удаляем их из словаря
    if notifications:
        for employer, employer_data in notifications.items():
            for data in employer_data:
                info_type = data["type"]
                days_left = data["days_left"]
                message = f"Через {days_left} у вас заканчивается {info_type}"
                await bot.send_message(chat_id=employer, text=message)

            # Удаляем уведомления для этого сотрудника после отправки
            del notifications[employer]


async def process_document(car, doc_field, doc_type, today, count_days, notifications, employer_id):
    doc_date_str = car.get(doc_field)
    if not doc_date_str:
        return

    try:
        try:
            doc_date = datetime.strptime(doc_date_str, "%Y-%m-%d")
        except ValueError:
            doc_date = datetime.strptime(doc_date_str, "%d.%m.%Y")

        days_left = (doc_date - today).days
        print(f"Проверка {doc_type}: {doc_date_str}, осталось дней: {days_left}")
        if days_left in count_days:
            if employer_id not in notifications:
                notifications[employer_id] = []
            notifications[employer_id].append({
                "type": doc_type,
                "days_left": days_left
            })
    except ValueError as e:
        print(f"Invalid date format for {doc_field}: {doc_date_str}, error: {e}")


async def send_notifications(notifications):
    for employer_id, employer_data in notifications.items():
        try:
            for data in employer_data:
                message = f"Через {data['days_left']} дней у вас заканчивается {data['type']}"
                await bot.send_message(chat_id=employer_id, text=message)
        except Exception as e:
            print(f"Failed to send message to {employer_id}: {e}")
