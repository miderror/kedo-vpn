import re

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.utils.db import get_or_create_user

from .menu import show_main_menu

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, bot):
    referrer_id = None
    match = re.search(r"/start (\d+)", message.text)
    if match:
        referrer_id = int(match.group(1))

    user, created = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        referred_by_id=referrer_id,
    )

    await show_main_menu(message, user, user.subscription, bot)
