from aiogram.types import BotCommand


async def set_main_menu(bot):
    # Создаем список команд
    main_menu_commands = [
        BotCommand(command="/menu", description="Role menu"),
        BotCommand(command="/orders", description="Available work orders"),
        BotCommand(command="/clients", description="List of clients and cars"),
        BotCommand(command="/finance", description="Entering financial information"),
        BotCommand(command="/languages", description="You can choice languages")
    ]
    await bot.set_my_commands(main_menu_commands)
