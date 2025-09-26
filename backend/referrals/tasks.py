import asyncio
import logging

from aiogram import Bot
from aiogram.enums import ParseMode
from celery import shared_task
from django.conf import settings
from django.db import transaction

from backend.payments.models import Payment
from backend.vpn.models import Subscription
from backend.vpn.tasks import ensure_vpn_client_active_task

from .models import ReferralBonus, ReferralTier

logger = logging.getLogger(__name__)


async def send_notification_async(telegram_id: int, text: str):
    from bot.keyboards.inline_keyboards import get_dismiss_kb

    bot = Bot(token=settings.BOT_TOKEN)
    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_dismiss_kb(text="Ок"),
        )
        logger.info(f"Уведомление о реф. бонусе успешно отправлено {telegram_id}")
    except Exception as e:
        logger.error(
            f"Не удалось отправить уведомление о реф. бонусе {telegram_id}: {e}"
        )
    finally:
        await bot.session.close()


@shared_task
def send_bonus_notification_task(referrer_telegram_id: int, bonus_days: int):
    text = (
        f"Класс! За реферальную активность на Ваш лицевой счет начислено "
        f"{bonus_days} бонусных дней."
    )
    asyncio.run(send_notification_async(referrer_telegram_id, text))


@shared_task
def process_referral_bonus_for_payment(payment_id: int):
    try:
        payment = Payment.objects.select_related("user", "user__referred_by").get(
            id=payment_id
        )
    except Payment.DoesNotExist:
        logger.warning(
            f"Платеж с ID {payment_id} не найден для начисления реф. бонуса."
        )
        return

    buyer = payment.user
    referrer = buyer.referred_by

    if not referrer or referrer == buyer:
        return

    tier = (
        ReferralTier.objects.filter(
            min_payment_amount__lte=payment.amount, is_active=True
        )
        .order_by("-min_payment_amount")
        .first()
    )

    if not tier:
        logger.info(
            f"Для платежа {payment.id} на сумму {payment.amount} не найден подходящий реф. уровень."
        )
        return

    bonus_days_to_award = tier.bonus_days

    try:
        with transaction.atomic():
            referrer_subscription = Subscription.objects.select_for_update().get(
                user=referrer
            )
            was_active_before_bonus = referrer_subscription.is_active
            referrer_subscription.extend_subscription(days=bonus_days_to_award)

            ReferralBonus.objects.create(
                referrer=referrer,
                referral=buyer,
                triggering_payment=payment,
                bonus_days_awarded=bonus_days_to_award,
            )

        if not was_active_before_bonus:
            referrer_subscription.refresh_from_db()
            if referrer_subscription.is_active:
                logger.info(
                    f"Подписка реферера {referrer.telegram_id} была неактивна. Активируем клиента в 3x-ui."
                )
                ensure_vpn_client_active_task.delay(referrer_subscription.id)

        logger.info(
            f"Начислен бонус {bonus_days_to_award} дней для {referrer.telegram_id} за покупку от {buyer.telegram_id}"
        )

        send_bonus_notification_task.delay(referrer.telegram_id, bonus_days_to_award)

    except Subscription.DoesNotExist:
        logger.error(
            f"Не найдена подписка для реферера {referrer.telegram_id} для начисления бонуса."
        )
    except Exception as e:
        logger.exception(
            f"Ошибка при начислении реф. бонуса для платежа {payment.id}: {e}"
        )
