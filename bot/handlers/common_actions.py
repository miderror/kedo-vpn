from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from bot.keyboards.callbacks import NotificationCallback

router = Router()


@router.callback_query(NotificationCallback.filter(F.action == "dismiss"))
async def dismiss_message_handler(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except TelegramBadRequest as e:
        print(f"Не удалось удалить сообщение: {e}")
    finally:
        await callback.answer()
