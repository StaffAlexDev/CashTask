from datetime import datetime
from pathlib import Path

from config.constants import PHOTOS_DIR


def get_month_year_folder(base_dir=PHOTOS_DIR):
    """Создает папку в формате ГГГГ-ММ (например, 2024-05) и возвращает её путь."""
    now = datetime.now()
    folder_name = now.strftime("%Y-%m")
    folder_path = Path(base_dir) / folder_name
    folder_path.mkdir(parents=True, exist_ok=True)  # Создаем все родительские директории при необходимости
    return str(folder_path)
