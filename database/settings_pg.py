import os

import asyncpg
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

DB_CONFIG = {
    'user': os.getenv("POSTGRES_USER"),
    'password': os.getenv("POSTGRES_PASSWORD"),
    'database': os.getenv("POSTGRES_DB"),
    'host': 'localhost',
    'port': 5432
}


async def get_db_connection():
    return await asyncpg.connect(**DB_CONFIG)
