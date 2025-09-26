from typing import Tuple

from asgiref.sync import sync_to_async
from django.db import transaction
from django.utils import timezone

from backend.content.models import BotTexts, SiteSettings
from backend.payments.models import Payment as PaymentModel
from backend.referrals.tasks import process_referral_bonus_for_payment
from backend.sender.models import Broadcast
from backend.users.models import User
from backend.vpn.models import Subscription, Tariff
from backend.vpn.tasks import ensure_vpn_client_active_task


@sync_to_async
def get_or_create_user(
    telegram_id: int, username: str, referred_by_id: int = None
) -> Tuple[User, bool]:
    referrer = None
    if referred_by_id:
        try:
            referrer = User.objects.get(telegram_id=referred_by_id)
            if referrer.telegram_id == telegram_id:
                referrer = None
        except User.DoesNotExist:
            referrer = None

    with transaction.atomic():
        user, created = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={"username": username, "referred_by": referrer},
        )
        if created:
            Subscription.objects.create(user=user, end_date=timezone.now())

    user_with_subscription = User.objects.select_related("subscription").get(
        telegram_id=telegram_id
    )
    return user_with_subscription, created


@sync_to_async
def get_user_with_subscription(telegram_id: int):
    try:
        return User.objects.select_related("subscription").get(telegram_id=telegram_id)
    except User.DoesNotExist:
        return None


@sync_to_async
def get_active_tariffs():
    return list(Tariff.objects.filter(is_active=True).order_by("order"))


@sync_to_async
def get_tariff_by_id(tariff_id: int):
    try:
        return Tariff.objects.get(id=tariff_id)
    except Tariff.DoesNotExist:
        return None


@sync_to_async
def create_payment_record(
    user: User, tariff: Tariff, payment_id_provider: str
) -> PaymentModel:
    payment = PaymentModel.objects.create(
        user=user,
        tariff=tariff,
        amount=tariff.price,
        payment_id_provider=payment_id_provider,
        status=PaymentModel.Status.PENDING,
    )
    return payment


@sync_to_async
def get_pending_payment(payment_id_provider: str):
    try:
        return PaymentModel.objects.select_related("user", "tariff").get(
            payment_id_provider=payment_id_provider, status=PaymentModel.Status.PENDING
        )
    except PaymentModel.DoesNotExist:
        return None


@sync_to_async
def process_successful_payment(payment: PaymentModel):
    with transaction.atomic():
        subscription = Subscription.objects.select_for_update().get(user=payment.user)

        subscription.extend_subscription(days=payment.tariff.duration_days)
        subscription.total_paid += payment.amount
        subscription.save(update_fields=["total_paid"])

        payment.status = PaymentModel.Status.SUCCEEDED
        payment.save()

        if not subscription.is_vpn_client_active:
            ensure_vpn_client_active_task.delay(subscription.id)

    process_referral_bonus_for_payment.delay(payment.id)


@sync_to_async
@transaction.atomic
def activate_trial_subscription(subscription_id: int) -> bool:
    try:
        sub = Subscription.objects.select_for_update().get(id=subscription_id)
        if sub.trial_activated:
            return True

        sub.extend_subscription(days=2)

        sub.trial_activated = True
        sub.save(update_fields=["trial_activated"])

        ensure_vpn_client_active_task.delay(sub.id)
        return True
    except Subscription.DoesNotExist:
        return False


@sync_to_async
def get_support_link():
    settings, _ = SiteSettings.objects.get_or_create(pk=1)
    return settings.support_link


@sync_to_async
def update_broadcast_status_db(broadcast_id: int, status: str):
    try:
        Broadcast.objects.filter(pk=broadcast_id).update(status=status)
        return True
    except Exception:
        return False


@sync_to_async
def get_bot_texts():
    texts, _ = BotTexts.objects.get_or_create(pk=1)
    return texts
