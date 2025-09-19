from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from bot.utils.db import get_user_with_subscription


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        user = await get_user_with_subscription(event.from_user.id)

        if user:
            data["user"] = user
            data["subscription"] = user.subscription
            return await handler(event, data)

        if (
            isinstance(event, Message)
            and event.text
            and event.text.startswith("/start")
        ):
            return await handler(event, data)

        return
