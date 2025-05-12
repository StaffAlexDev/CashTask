import os
from contextlib import contextmanager

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


@contextmanager
def google_sheet_client():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(os.getenv("SERVICE_ACCOUNT_FILE"), scope)
    client = gspread.authorize(creds)

    try:
        yield client
    finally:
        pass


# Получаем или создаём таблицу
def get_google_sheet(client):
    try:
        spreadsheet = client.open(os.getenv("EXCEL_NAME"))
    except gspread.SpreadsheetNotFound:
        spreadsheet = client.create(os.getenv("EXCEL_NAME"))
        spreadsheet.share(os.getenv("EMAIL_ADDRESS"), perm_type='user', role='writer')

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
    with google_sheet_client() as client:
        spreadsheet = get_google_sheet(client)
        worksheet = get_or_create_monthly_sheet(spreadsheet)

        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        worksheet.append_row([current_date, amount, record_type, description])


if __name__ == '__main__':
    text = " 500 расход, такси"
    parts = text.split()
    record_types = parts[1]
    amounts = int(parts[0])
    descriptions = " ".join(parts[2:])

    add_record_to_sheet(amounts, record_types, descriptions)
    print("✅ Запись добавлена!")
