import random
import string


def generate_temp_key(length: int = 32) -> str:
    """
    Генерация безопасного временного ключа.
    Используются только цифры и буквы.
    """
    allowed_chars = string.ascii_letters + string.digits
    return ''.join(random.choice(allowed_chars) for _ in range(length))
