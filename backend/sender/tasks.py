import asyncio
import logging
from datetime import timedelta

from aiogram import Bot
from aiogram.exceptions import (
    TelegramAPIError,
    TelegramBadRequest,
    TelegramForbiddenError,
)
from aiogram.types import FSInputFile, Message
from asgiref.sync import sync_to_async
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from backend.content.models import BroadcastSettings
from backend.users.models import User
from bot.keyboards.inline_keyboards import get_broadcast_approval_kb

from .models import Broadcast, SentBroadcastMessage

logger = logging.getLogger(__name__)


async def send_media_or_text(
    bot: Bot, chat_id: int, broadcast: Broadcast, keyboard=None
) -> Message | None:
    try:
        if broadcast.media_file and broadcast.media_type:
            file = FSInputFile(broadcast.media_file.path)
            media_type = broadcast.media_type
            sender_map = {
                Broadcast.MediaType.PHOTO: bot.send_photo,
                Broadcast.MediaType.VIDEO: bot.send_video,
                Broadcast.MediaType.DOCUMENT: bot.send_document,
                Broadcast.MediaType.AUDIO: bot.send_audio,
            }
            sender = sender_map.get(media_type)
            if sender:
                return await sender(
                    chat_id, file, caption=broadcast.text, reply_markup=keyboard
                )
        else:
            return await bot.send_message(
                chat_id, broadcast.text, reply_markup=keyboard
            )
    except TelegramForbiddenError:
        logger.warning(
            f"Не удалось отправить сообщение пользователю {chat_id} (заблокировал бота)."
        )
    except (TelegramAPIError, TelegramBadRequest) as e:
        logger.error(f"Не удалось отправить сообщение пользователю {chat_id}: {e}")
    return None


@shared_task
def send_broadcast_for_approval_task(broadcast_id: int):
    asyncio.run(send_broadcast_for_approval_async(broadcast_id))


async def send_broadcast_for_approval_async(broadcast_id: int):
    try:
        settings_obj = await BroadcastSettings.objects.select_related(
            "broadcast_admin"
        ).aget(pk=1)
        admin = settings_obj.broadcast_admin
        if not admin:
            logger.error(
                f"Рассылка {broadcast_id}: не назначен администратор для подтверждения."
            )
            await Broadcast.objects.filter(pk=broadcast_id).aupdate(
                status=Broadcast.Status.ERROR
            )
            return

        broadcast = await Broadcast.objects.aget(id=broadcast_id)
        bot = Bot(token=settings.BOT_TOKEN)
        keyboard = get_broadcast_approval_kb(broadcast_id)

        await send_media_or_text(bot, admin.telegram_id, broadcast, keyboard)
        await bot.session.close()
        logger.info(
            f"Рассылка {broadcast_id} отправлена на подтверждение администратору {admin.telegram_id}."
        )

    except (Broadcast.DoesNotExist, BroadcastSettings.DoesNotExist):
        logger.error(f"Рассылка или настройки не найдены для ID: {broadcast_id}")
    except Exception as e:
        logger.exception(
            f"Ошибка при отправке рассылки {broadcast_id} на подтверждение: {e}"
        )
        await Broadcast.objects.filter(pk=broadcast_id).aupdate(
            status=Broadcast.Status.ERROR
        )


@shared_task
def start_mass_broadcast_task(broadcast_id: int):
    asyncio.run(run_mass_broadcast_async(broadcast_id))


async def run_mass_broadcast_async(broadcast_id: int):
    try:
        broadcast = await Broadcast.objects.aget(id=broadcast_id)
        broadcast.status = Broadcast.Status.APPROVED
        await broadcast.asave(update_fields=["status"])

        users_to_send = await sync_to_async(list)(User.objects.all())
        if not users_to_send:
            logger.warning(f"Рассылка {broadcast_id}: нет пользователей для отправки.")
            broadcast.status = Broadcast.Status.ERROR
            await broadcast.asave(update_fields=["status"])
            return

        bot = Bot(token=settings.BOT_TOKEN)

        for user in users_to_send:
            message = await send_media_or_text(bot, user.telegram_id, broadcast)
            if message:
                await SentBroadcastMessage.objects.acreate(
                    broadcast=broadcast, user=user, message_id=message.message_id
                )

        await bot.session.close()
        broadcast.status = Broadcast.Status.SENT
        await broadcast.asave(update_fields=["status"])
        logger.info(f"Рассылка {broadcast_id} успешно отправлена всем пользователям.")

    except Broadcast.DoesNotExist:
        logger.error(f"Рассылка с ID {broadcast_id} не найдена для массовой отправки.")
    except Exception as e:
        logger.exception(
            f"Критическая ошибка при выполнении массовой рассылки {broadcast_id}: {e}"
        )
        await Broadcast.objects.filter(pk=broadcast_id).aupdate(
            status=Broadcast.Status.ERROR
        )


@shared_task
def delete_old_broadcast_messages_task():
    asyncio.run(delete_old_broadcast_messages_async())


async def delete_old_broadcast_messages_async():
    time_threshold = timezone.now() - timedelta(hours=24)
    messages_to_delete = await sync_to_async(list)(
        SentBroadcastMessage.objects.filter(sent_at__lt=time_threshold).select_related(
            "user"
        )
    )
    if not messages_to_delete:
        return

    logger.info(f"Найдено {len(messages_to_delete)} сообщений для удаления.")
    bot = Bot(token=settings.BOT_TOKEN)

    for sent_msg in messages_to_delete:
        try:
            await bot.delete_message(
                chat_id=sent_msg.user.telegram_id, message_id=sent_msg.message_id
            )
        except (TelegramAPIError, TelegramBadRequest) as e:
            logger.warning(
                f"Не удалось удалить сообщение {sent_msg.message_id} для пользователя {sent_msg.user.telegram_id}: {e}"
            )
        finally:
            await sent_msg.adelete()

    await bot.session.close()
    logger.info("Задача по удалению старых сообщений рассылки завершена.")
