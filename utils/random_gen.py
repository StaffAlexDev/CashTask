import random
import string
import secrets


def generate_temp_data_key(length: int = 12) -> str:
    """
    Генерация безопасного временного ключа.
    Используются только цифры и буквы.
    """
    allowed_chars = string.ascii_letters + string.digits
    return ''.join(random.choice(allowed_chars) for _ in range(length))


def generate_invite_code() -> str:
    """
        Генерация безопасного ключа фирмы для добавления сотрудников.
        Используются только цифры и буквы.
        """
    invite_code = secrets.token_urlsafe(8)
    return invite_code
