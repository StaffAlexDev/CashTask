from datetime import datetime

from config.patterns import COUNT_DAYS
from database.employees_pg import get_employees_cars
from settings import bot


async def checking_the_end_date_of_documents():
    employer_cars = await get_employees_cars()
    today = datetime.today()
    notifications = {}

    for car in employer_cars:

        # Проверяем страховку
        result = await process_document(car, "insurance", "страховка", today, COUNT_DAYS)
        for key, messages in result.items():
            notifications.setdefault(key, []).extend(messages)

        # Проверяем техосмотр
        result = await process_document(car, "technical_inspection", "техосмотр", today, COUNT_DAYS)
        for key, messages in result.items():
            notifications.setdefault(key, []).extend(messages)

    if notifications:
        await send_notifications(notifications)


async def process_document(car, date_key, display_name, today, count_days):
    notifications = {}

    expire_date = car.get(date_key)
    if not expire_date:
        return notifications

    expire_date = datetime.strptime(expire_date, "%Y-%m-%d")
    days_left = (expire_date - today).days

    if 0 <= days_left <= count_days:
        employer_id = car.get("employer_id")
        notifications.setdefault(employer_id, []).append(
            f"{display_name} для автомобиля {car.get('brand')} {car.get('state_number')} истекает: "
            f"{expire_date.strftime('%d.%m.%Y')} ({days_left} дн. осталось)"
        )

    return notifications


async def send_notifications(notifications):
    for employer_id, employer_data in notifications.items():
        try:
            for data in employer_data:
                message = f"Через {data['days_left']} дней у вас заканчивается {data['type']}"
                await bot.send_message(chat_id=employer_id, text=message)
        except Exception as e:
            print(f"Failed to send message to {employer_id}: {e}")
