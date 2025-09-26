import urllib.parse

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery

from bot.keyboards.callbacks import MenuCallback
from bot.keyboards.inline_keyboards import get_earn_kb
from bot.utils.db import get_bot_texts

router = Router()


@router.callback_query(MenuCallback.filter(F.action == "earn"))
async def earn_handler(callback: CallbackQuery, bot: Bot):
    bot_info = await bot.get_me()
    user_id = callback.from_user.id

    raw_referral_link = f"https://t.me/{bot_info.username}?start={user_id}"

    encoded_link = urllib.parse.quote(raw_referral_link, safe="")
    share_url = f"https://t.me/share/url?url={encoded_link}"

    texts = await get_bot_texts()
    text = texts.referral_earn_info

    keyboard = get_earn_kb(share_url)

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()
