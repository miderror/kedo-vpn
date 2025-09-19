from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery

from bot.keyboards.callbacks import MenuCallback
from bot.keyboards.inline_keyboards import get_earn_kb

router = Router()


@router.callback_query(MenuCallback.filter(F.action == "earn"))
async def earn_handler(callback: CallbackQuery, bot: Bot):
    bot_info = await bot.get_me()
    user_id = callback.from_user.id

    referral_link = f"https://t.me/{bot_info.username}?start={user_id}"

    text = (
        "Отправьте человеку реферальный профиль и заработайте "
        "от 50 до 200 дней на свой лицевой счет от каждой покупки пользователя"
    )

    keyboard = get_earn_kb(referral_link)

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()
