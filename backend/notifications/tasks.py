import asyncio
import logging
from datetime import timedelta

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from backend.vpn.models import Subscription
from backend.vpn.tasks import deactivate_vpn_client_task
from bot.keyboards.inline_keyboards import get_subscription_reminder_kb

from .models import NotificationRule, SentNotification

logger = logging.getLogger(__name__)


async def send_message_async(telegram_id: int, text: str, keyboard=None):
    bot = Bot(token=settings.BOT_TOKEN)
    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )
        logger.info(f"Сообщение успешно отправлено пользователю {telegram_id}")
        return True
    except TelegramAPIError as e:
        logger.error(f"Не удалось отправить сообщение пользователю {telegram_id}: {e}")
        return False
    finally:
        await bot.session.close()


@shared_task
def send_telegram_notification_task(
    telegram_id: int, text: str, with_keyboard: bool = False
):
    keyboard = get_subscription_reminder_kb() if with_keyboard else None
    asyncio.run(send_message_async(telegram_id, text, keyboard))


@shared_task
def check_and_deactivate_expired_subscriptions():
    now = timezone.now()
    expired_subscriptions = Subscription.objects.filter(
        end_date__lte=now, is_vpn_client_active=True
    )

    for sub in expired_subscriptions:
        logger.info(f"Подписка для user_id={sub.user.telegram_id} истекла. Отключаем.")
        deactivate_vpn_client_task.delay(sub.id)

        sub.is_vpn_client_active = False
        sub.save(update_fields=["is_vpn_client_active"])

        message = "Обращаем внимание, Ваша подписка закончилась и vpn остановлен! Докупите дней и подписка останется активной!"
        send_telegram_notification_task.delay(
            sub.user.telegram_id, message, with_keyboard=True
        )


@shared_task
def send_expiry_reminders():
    now = timezone.now()
    active_rules = NotificationRule.objects.filter(is_active=True)

    for rule in active_rules:
        trigger_time_start = now + timedelta(hours=rule.trigger_hours_before_expiry)
        trigger_time_end = trigger_time_start + timedelta(minutes=10)

        subscriptions_to_notify = Subscription.objects.filter(
            end_date__range=(trigger_time_start, trigger_time_end)
        )

        for sub in subscriptions_to_notify:
            already_sent = SentNotification.objects.filter(
                user=sub.user,
                rule=rule,
                subscription_end_date_at_send_time=sub.end_date,
            ).exists()

            if not already_sent:
                days_left = (sub.end_date - now).days
                hours_left = int(((sub.end_date - now).total_seconds() % 86400) / 3600)

                message = rule.message_template.format(days=days_left, hours=hours_left)

                send_telegram_notification_task.delay(
                    sub.user.telegram_id, message, with_keyboard=True
                )

                SentNotification.objects.create(
                    user=sub.user,
                    rule=rule,
                    subscription_end_date_at_send_time=sub.end_date,
                )
                logger.info(
                    f"Отправлено уведомление по правилу '{rule.name}' для user_id={sub.user.telegram_id}"
                )
