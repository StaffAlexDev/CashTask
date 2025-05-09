from aiogram import Dispatcher

from middlewares.inject import UserInjectMiddleware


def setup_middlewares(dp: Dispatcher):
    """
    Регистрирует все мидлвари в правильном порядке.
    """
    dp.update.middleware(UserInjectMiddleware())
