from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from backend.sender.models import Broadcast
from backend.sender.tasks import start_mass_broadcast_task
from bot.keyboards.callbacks import BroadcastAdminCallback
from bot.utils.db import update_broadcast_status_db

router = Router()


@router.callback_query(BroadcastAdminCallback.filter(F.action == "approve"))
async def approve_broadcast_handler(
    callback: CallbackQuery, callback_data: BroadcastAdminCallback
):
    await callback.answer("✅ Рассылка одобрена и поставлена в очередь на отправку.")

    start_mass_broadcast_task.delay(callback_data.broadcast_id)

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass


@router.callback_query(BroadcastAdminCallback.filter(F.action == "decline"))
async def decline_broadcast_handler(
    callback: CallbackQuery, callback_data: BroadcastAdminCallback
):
    await callback.answer("❌ Рассылка отклонена.")

    await update_broadcast_status_db(
        callback_data.broadcast_id, Broadcast.Status.CANCELED
    )

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
