from aiogram import BaseMiddleware

from database.state_models import UserCookies


class UserMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = event.from_user.id
        user = UserCookies(user_id)
        data['user'] = user
        data['role'] = user.get_role()
        return await handler(event, data)
