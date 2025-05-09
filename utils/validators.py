import re
from datetime import datetime
from typing import Optional

from config.patterns import LICENSE_PLATE_PATTERNS, PHONE_PATTERN, DATE_PATTERN, BRAND_PATTERN, MODEL_PATTERN, \
    VIN_PATTERN, NAME_PATTERN, SOCIAL_PATTERN, PAYMENT_TYPE_PATTERNS


def is_likely_license_plate(text: str) -> bool:
    """
        Проверяет, похож ли текст на номерной знак (Европа + Беларусь/Украина).
        Возвращает True, если это номер, а не модель авто.
        """
    if not text:
        return False

    text_clean = re.sub(r'[\s-]', '', text).upper()
    for pattern in LICENSE_PLATE_PATTERNS:  # Берём из constants.py
        if re.match(pattern, text_clean):
            return True
    return False


def is_phone_number(phone: str) -> bool:
    return bool(re.match(PHONE_PATTERN, normalize_number(phone)))


def is_date(text: str) -> bool:
    """Проверка текста на корректность даты"""
    return bool(re.match(DATE_PATTERN, normalize_date(text)))


def validate_car_data(owner_type: str, data: dict) -> dict:
    """Проверка данных автомобиля с учётом типа владельца.

    Args:
        owner_type: "client" или "employer"
        data: {
            "brand": str,
            "model": str,
            "license_plate": str,  # Проверяется is_likely_license_plate()
            "vin_code": str,       # Опционально
            "tech_date": str,      # Только для employer
            "ins_date": str        # Только для employer
        }

    Returns:
        {"status": "ok"} или {"status": "error", "errors": [{"field": ..., "error": ...}]}
    """
    errors = []

    # Проверка марки и модели
    if not re.match(BRAND_PATTERN, data.get("brand", "")):
        errors.append({"field": "brand", "error": "Некорректная марка."})

    if not re.match(MODEL_PATTERN, data.get("model", "")):
        errors.append({"field": "model", "error": "Некорректная модель."})

    # Проверка номера (используем твою функцию)
    license_plate = data.get("license_plate", "")
    if not license_plate or not is_likely_license_plate(license_plate):
        errors.append({"field": "license_plate", "error": "Неверный формат номера."})

    # Проверка VIN (если передан)
    if "vin_code" in data and not re.match(VIN_PATTERN, data["vin_code"]):
        errors.append({"field": "vin_code", "error": "Неверный VIN."})

    # Доп. проверки для сотрудников
    if owner_type == "employer":
        if not is_date(data.get("tech_date")):
            errors.append({"field": "tech_date", "error": "Неверная дата ТО."})
        if not is_date(data.get("ins_date")):
            errors.append({"field": "ins_date", "error": "Неверная дата страховки."})

    return {"status": "ok"} if not errors else {"status": "error", "errors": errors}


def validate_contact(text: str) -> dict:
    """Проверяет строку 'Имя Фамилия, телефон, соцсеть' (соцсеть или телефон можно опустить)."""
    parts = [part.strip() for part in text.split(",", maxsplit=2)]
    if len(parts) < 2:
        return {"status": "error",
                "field": "all",
                "error": "Используйте формат: 'Имя Фамилия, телефон, соцсеть' (соцсеть или телефон можно опустить)"}

    name_part, *contact_parts = parts  # Имя, [телефон, соцсеть]

    # Проверка имени и фамилии (любые буквы, 2-20 символов)
    if not re.match(NAME_PATTERN, name_part):
        return {"status": "error", "field": "name", "error": "Некорректное имя или фамилия"}

    # Проверка контактов (телефон и/или соцсеть)
    errors = []
    for contact in contact_parts:
        if not contact:
            continue
        if is_phone_number(contact):
            continue
        elif re.match(
            SOCIAL_PATTERN,
            contact,
            re.IGNORECASE
        ):
            continue
        else:
            errors.append(contact)

    if errors:
        return {"status": "error", "field": "contact", "error": f"Некорректные контакты: {', '.join(errors)}"}
    return {"status": "ok"}


def normalize_payment_type(raw: str) -> Optional[str]:
    raw = raw.lower().replace(" ", "")

    for payment_type, patterns in PAYMENT_TYPE_PATTERNS.items():
        for pattern in patterns:
            if pattern in raw:
                return payment_type

    return None


def normalize_number(phone: str) -> str:
    phone = phone.strip()
    phone = re.sub(r"[^\d+]", "", phone)
    if phone.startswith('+'):
        phone = '+' + re.sub(r"[^\d]", "", phone[1:])
    else:
        phone = re.sub(r"[^\d]", "", phone)
    return phone


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
