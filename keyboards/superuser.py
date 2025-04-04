from aiogram.utils.keyboard import InlineKeyboardBuilder


def period_by_report_kb():
    buttons = {
        "day": {"text": "День", "callback_data": "day"},
        "week": {"text": "Неделя", "callback_data": "week"},
        "two_weeks": {"text": "Две недели", "callback_data": "two_weeks"},
        "month": {"text": "Месяц", "callback_data": "month"},
        "all": {"text": "За все время", "callback_data": "all"},
    }
    builder = InlineKeyboardBuilder()

    for btn in buttons:
        builder.button(text=buttons[btn].get("text"), callback_data=f"period_{buttons[btn].get("callback_data")}")
    builder.adjust(2)
    return builder.as_markup()
