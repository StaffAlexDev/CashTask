from aiogram.utils.keyboard import InlineKeyboardBuilder

from config.buttons_config import PERIOD_BUTTONS


def period_by_report_kb():
    builder = InlineKeyboardBuilder()

    for btn in PERIOD_BUTTONS:
        builder.button(text=PERIOD_BUTTONS[btn].get("text"),
                       callback_data=f"period_{PERIOD_BUTTONS[btn].get("callback_data")}")

    builder.adjust(2)

    return builder.as_markup()



