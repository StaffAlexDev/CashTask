from aiogram.types import BotCommand


async def set_main_menu(bot):
    # Создаем список команд
    main_menu_commands = [
        BotCommand(command="/start", description="Start menu"),
        BotCommand(command="/finance", description="finance"),
        BotCommand(command="/languages", description="languages")
    ]
    await bot.set_my_commands(main_menu_commands)
