from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PHOTOS_DIR = BASE_DIR / "data/receipts"
LANGUAGE_DIR = BASE_DIR / "languages"
DB_PATH = BASE_DIR / "database/cash_task.db"
