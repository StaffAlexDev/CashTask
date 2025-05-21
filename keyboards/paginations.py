from typing import List, Dict, Any, Callable

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.enums import Role


def build_paginated_keyboard(
        items: List[Dict[str, Any]],
        page: int = 1,
        items_per_page: int = 6,
        callback_prefix: str = "item",
        back_callback: str = "menu"
        ) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с пагинацией

    :param items: Список элементов для отображения
    :param page: Текущая страница
    :param items_per_page: Количество элементов на странице
    :param callback_prefix: Префикс для callback_data
    :param back_callback: Callback для кнопки "Назад"
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()

    # Вычисляем индексы для текущей страницы
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    paginated_items = items[start_idx:end_idx]

    # Добавляем кнопки элементов
    for item in paginated_items:
        builder.add(InlineKeyboardButton(
            text=item.get("button_text", str(item)),
            callback_data=f"{callback_prefix}_{page}_{item['id']}"
        ))

    # Добавляем кнопки пагинации
    navigation_buttons = []

    if page > 1:
        navigation_buttons.append(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"prev_{page}_{callback_prefix}"
        ))

    if end_idx < len(items):
        navigation_buttons.append(InlineKeyboardButton(
            text="Вперед ➡️",
            callback_data=f"next_{page}_{callback_prefix}"
        ))

    if navigation_buttons:
        builder.row(*navigation_buttons)

    # Кнопка возврата
    builder.row(InlineKeyboardButton(
        text="🔙 Выйти",
        callback_data=back_callback
    ))

    builder.adjust(1, repeat=True)
    return builder.as_markup()


def get_paginated_list(
    config: Dict[str, Any],
    page: int = 1,
    per_page: int = 6
) -> tuple[str, InlineKeyboardMarkup]:
    # 1. Достаем функцию и фильтры
    get_items_func: Callable = config["get_items_func"]
    filters: dict = config.get("filters", {})

    # 2. Вызываем её с фильтрами
    items = get_items_func(**filters)

    # 3. Форматируем для пагинации
    formatted_items = [
        {
            "id": item.get("id")
                  or item.get("client_id")
                  or item.get("car_id")
                  or item.get("order_id")
                  or item.get("task_id"),
            "button_text": config["build_button_text"](item),
            "raw_data": item
        }
        for item in items
    ]

    # 4. Строим клавиатуру
    keyboard = build_paginated_keyboard(
        items=formatted_items,
        page=page,
        items_per_page=per_page,
        callback_prefix=config["key"],      # например, храните key в конфиге
        back_callback=config["back_callback"]
    )

    text = f"{config['title']} (Страница {page}):"
    return text, keyboard


def action_with_item(item_type: str, item_id: int, page: int, role: Role) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="✏ Изменить",
            callback_data=f"item_{item_type}_{item_id}_edit"
        ),
        InlineKeyboardButton(
            text="🗑 Удалить",
            callback_data=f"item_{item_type}_{item_id}_delete"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="⬅ Назад",
            callback_data=f"back_to_list_{item_type}_{page}"
        )
    )
    if role == Role.SUPERADMIN:
        builder.row(
            InlineKeyboardButton(
                text="♻ Восстановить",
                callback_data=f"item_{item_type}_{item_id}_restore"
            )
        )

    return builder.as_markup()
