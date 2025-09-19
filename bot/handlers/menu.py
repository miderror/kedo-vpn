from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, Message

from backend.users.models import User
from backend.vpn.models import Subscription
from bot.keyboards.callbacks import MenuCallback
from bot.keyboards.inline_keyboards import get_main_menu_kb
from bot.utils.text_helpers import pluralize_days

router = Router()


async def show_main_menu(
    event: Message | CallbackQuery, user: User, subscription: Subscription, bot: Bot
):
    bot_info = await bot.get_me()

    days_remaining = subscription.days_remaining
    if not subscription.trial_activated:
        days_remaining += 2
    days_word = pluralize_days(days_remaining)
    text = f"ВАША ПОДПИСКА {days_remaining} {days_word}"

    keyboard = await get_main_menu_kb(user.telegram_id, bot_info.username)

    if isinstance(event, Message):
        await event.answer(text, reply_markup=keyboard)
    elif isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(MenuCallback.filter(F.action == "main_menu"))
async def back_to_main_menu_handler(
    callback: CallbackQuery, user: User, subscription: Subscription, bot: Bot
):
    await show_main_menu(callback, user, subscription, bot)
    await callback.answer()
