import os
import re
from pathlib import Path

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


bot = Bot(
    token=os.getenv("BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)


USER_ROLES = ['worker', 'admin', 'supervisor']
BASE_DIR = Path(__file__).parent
PHOTOS_DIR = BASE_DIR / "receipts"
INVOICE_PATTERN = re.compile(r"(-?\d{1,5})\s+(расход|приход)\s*,?\s*(.+)", re.IGNORECASE)
