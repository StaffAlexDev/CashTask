from aiogram import BaseMiddleware, types
from typing import Any, Callable, Dict, Awaitable

from models.state_models import UserContext


class UserInjectMiddleware(BaseMiddleware):
    """
    Middleware, которая добавляет в data объект UserContext.
    """

    async def __call__(
        self,
        handler: Callable[[types.Update, Dict[str, Any]], Awaitable[Any]],
        event: types.Update,
        data: Dict[str, Any],
    ) -> Any:

        user_id = None

        if event.message and event.message.from_user:
            user_id = event.message.from_user.id
        elif event.callback_query and event.callback_query.from_user:
            user_id = event.callback_query.from_user.id
        elif event.inline_query and event.inline_query.from_user:
            user_id = event.inline_query.from_user.id
        elif event.chat_member and event.chat_member.from_user:
            user_id = event.chat_member.from_user.id

        if user_id:
            user = UserContext(user_id)
            await user.load_from_db()
            data["user"] = user

        return await handler(event, data)
