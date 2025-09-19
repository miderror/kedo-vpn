import uuid

from django.db import models

from backend.payments.models import Payment
from backend.users.models import User


class ReferralTier(models.Model):
    name = models.CharField(
        max_length=100, verbose_name="Название уровня (для админки)"
    )
    min_payment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Минимальная сумма покупки реферала (руб)",
        help_text="Бонус будет начислен, если сумма покупки равна или больше этого значения.",
        unique=True,
    )
    bonus_days = models.PositiveIntegerField(verbose_name="Бонусных дней для реферера")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    def __str__(self):
        return f"{self.name}: {self.bonus_days} дней за покупку от {self.min_payment_amount}₽"

    class Meta:
        verbose_name = "Уровень реферального бонуса"
        verbose_name_plural = "Уровни реферальных бонусов"
        ordering = ["min_payment_amount"]


class ReferralBonus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referrer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bonuses_given",
        verbose_name="Кто получил бонус (Реферер)",
    )
    referral = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bonuses_received_for",
        verbose_name="Чья покупка (Реферал)",
    )
    triggering_payment = models.OneToOneField(
        Payment, on_delete=models.CASCADE, verbose_name="Платеж, активировавший бонус"
    )
    bonus_days_awarded = models.PositiveIntegerField(
        verbose_name="Начислено бонусных дней"
    )
    awarded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата начисления")

    def __str__(self):
        return f"Бонус для {self.referrer} за платеж от {self.referral}"

    class Meta:
        verbose_name = "Реферальный бонус"
        verbose_name_plural = "Реферальные бонусы"
        ordering = ["-awarded_at"]
