import re

from datetime import datetime
from pathlib import Path

from config import PHOTOS_DIR, PHONE_PATTERN


def get_month_year_folder(base_dir=PHOTOS_DIR):
    """Создает папку в формате ГГГГ-ММ (например, 2024-05) и возвращает её путь."""
    now = datetime.now()
    folder_name = now.strftime("%Y-%m")
    folder_path = Path(base_dir) / folder_name
    folder_path.mkdir(parents=True, exist_ok=True)  # Создаем все родительские директории при необходимости
    return str(folder_path)


def dict_factory(cursor, row):
    """Хелпер для возврата результатов в виде словарей"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


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


def clean_phone_number(phone: str) -> str:
    phone = phone.strip()
    phone = re.sub(r"[^\d+]", "", phone)
    if phone.startswith('+'):
        phone = '+' + re.sub(r"[^\d]", "", phone[1:])
    else:
        phone = re.sub(r"[^\d]", "", phone)
    return phone


def is_phone_number(phone: str) -> bool:
    return bool(re.match(PHONE_PATTERN, phone))
