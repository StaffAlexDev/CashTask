import os

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


# Авторизация и получение таблицы
def get_google_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(os.getenv("SERVICE_ACCOUNT_FILE"), scope)
    client = gspread.authorize(creds)

    try:
        spreadsheet = client.open("1323 Service")
    except gspread.SpreadsheetNotFound:
        spreadsheet = client.create("1323 Service")
        spreadsheet.share('scherbakov.alexeii@gmail.com', perm_type='user', role='writer')

    return spreadsheet


# Получаем или создаём лист для текущего месяца
def get_or_create_monthly_sheet(spreadsheet):
    current_month = datetime.now().strftime("%Y-%m")

    try:
        worksheet = spreadsheet.worksheet(current_month)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=current_month, rows="1000", cols="10")
        worksheet.append_row(["Дата", "Сумма", "Тип", "Описание"])

    return worksheet


# Добавляем запись в текущий месячный лист
def add_record_to_sheet(amount: int, record_type: str, description: str):
    spreadsheet = get_google_sheet()
    worksheet = get_or_create_monthly_sheet(spreadsheet)

    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    worksheet.append_row([current_date, amount, record_type, description])


if __name__ == '__main__':
    text = " 500 расход, такси"
    parts = text.split()
    record_types = parts[1]  # "расход" или "приход"
    amounts = int(parts[0])  # сумма
    descriptions = " ".join(parts[2:])  # остальное — описание

    add_record_to_sheet(amounts, record_types, descriptions)
    print("✅ Запись добавлена!")
