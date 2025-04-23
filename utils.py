import asyncio
import base64
import re

from datetime import datetime
from pathlib import Path

from config import PHOTOS_DIR, PHONE_PATTERN, BRAND_PATTERN, MODEL_PATTERN, DATE_PATTERN, COUNT_DAYS
from database.db_crud import get_employees_cars
from settings import bot


def get_month_year_folder(base_dir=PHOTOS_DIR):
    """Создает папку в формате ГГГГ-ММ (например, 2024-05) и возвращает её путь."""
    now = datetime.now()
    folder_name = now.strftime("%Y-%m")
    folder_path = Path(base_dir) / folder_name
    folder_path.mkdir(parents=True, exist_ok=True)  # Создаем все родительские директории при необходимости
    return str(folder_path)


def is_likely_license_plate(text: str) -> bool:
    """
    Проверяет, похож ли текст на номерной знак (Европа + Беларусь/Украина).
    Возвращает True, если это номер, а не модель авто.
    """
    text_clean = re.sub(r'[\s-]', '', text).upper()

    plate_patterns = [
        # Литва, Латвия, Польша (AB1234, ABC123, 1234AB)
        r'^[A-Z]{2,3}\d{2,5}$',
        r'^\d{2,4}[A-Z]{2,3}$',

        # Германия, Франция (AB-123-CD, B XY 1234)
        r'^[A-Z]{1,3}\d{1,4}[A-Z]{0,2}$',

        # Временные номера (L123456, TR12345)
        r'^[A-Z]{1,2}\d{5,6}$',

        # Украина (AA1234BB)
        r'^[A-Z]{2}\d{4}[A-Z]{2}$',

        # Беларусь (1234AB1)
        r'^\d{4}[A-Z]{2}[1-7]$'
    ]

    is_plate = any(re.match(p, text_clean) for p in plate_patterns)

    has_letters = any(c.isalpha() for c in text_clean)
    has_digits = any(c.isdigit() for c in text_clean)

    return is_plate or (has_letters and has_digits)


def normalize_number(phone: str) -> str:
    phone = phone.strip()
    phone = re.sub(r"[^\d+]", "", phone)
    if phone.startswith('+'):
        phone = '+' + re.sub(r"[^\d]", "", phone[1:])
    else:
        phone = re.sub(r"[^\d]", "", phone)
    return phone


def is_phone_number(phone: str) -> bool:
    return bool(re.match(PHONE_PATTERN, phone))


def normalize_date(date_str: str) -> str | None:
    try:
        dt = datetime.strptime(date_str.strip(), "%d.%m.%y")

        if dt.year < 100:
            dt = dt.replace(year=dt.year + 2000)
        return dt.strftime("%d.%m.%Y")
    except ValueError:
        try:

            dt = datetime.strptime(date_str.strip(), "%d.%m.%Y")
            return dt.strftime("%d.%m.%Y")
        except ValueError:
            return None


def is_data(text: str) -> bool:
    return bool(re.match(DATE_PATTERN, normalize_date(text)))


def is_text_patterns(text: list) -> dict:

    if len(text) != 5:
        return {"status": "неверное количество полей."}
    else:
        brand, model, plate, tech_date, ins_date = text

        if not re.match(BRAND_PATTERN, brand):
            return {"status": "некорректная марка."}
        elif not re.match(MODEL_PATTERN, model):
            return {"status": "некорректная модель."}
        elif not is_data(tech_date):
            return {"status": "неверный формат даты ТО."}
        elif not is_data(ins_date):
            return {"status": "неверный формат даты страховки."}
        else:
            return {"status": "ok"}


async def checking_the_end_date_of_documents(stop_event: asyncio.Event):
    while not stop_event.is_set():
        try:
            employer_cars = get_employees_cars()
            today = datetime.today()
            notifications = {}

            for car in employer_cars:
                try:
                    employer_id = car["employer_id"]
                    if not employer_id:
                        continue

                    await process_document(
                        car, "technical_inspection", "техосмотр",
                        today, COUNT_DAYS, notifications, employer_id
                    )
                    await process_document(
                        car, "insurance", "страховка",
                        today, COUNT_DAYS, notifications, employer_id
                    )

                except Exception as e:
                    print(f"Error processing car {car}: {e}")
                    continue

            if notifications:
                await send_notifications(notifications)

            await asyncio.sleep(86400)  # Ждем 24 часа

        except Exception as e:
            print(f"Error in main loop: {e}")
            await asyncio.sleep(3600)


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


def str_encode(text: str) -> str:
    encoded = base64.b64encode(text.encode()).decode()
    return encoded


def str_decode(text: str) -> str:
    decoded = base64.b64decode(text.encode()).decode()
    return decoded
