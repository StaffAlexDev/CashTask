from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.enums import Period


def period_by_report_kb(lang_data: dict) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for btn in Period:  # type: Period
        builder.button(
            text=btn.display_name(lang_data),
            callback_data=f"period_{btn.value}"
        )

    builder.adjust(2)
    return builder.as_markup()



