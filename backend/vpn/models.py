import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone

from backend.users.models import User


class Tariff(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название тарифа (для админки)")
    duration_days = models.PositiveIntegerField(verbose_name="Длительность (дни)")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Цена (руб)"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")

    def __str__(self):
        return f"{self.name} ({self.duration_days} дней за {self.price} руб)"

    class Meta:
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"


class Subscription(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="subscription",
        verbose_name="Пользователь",
    )
    end_date = models.DateTimeField(verbose_name="Дата окончания")
    vless_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    trial_activated = models.BooleanField(
        default=False, verbose_name="Триал активирован"
    )

    total_paid = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Всего пополнено"
    )

    is_vpn_client_active = models.BooleanField(default=False, verbose_name="Клиент VPN активен")

    @property
    def is_active(self):
        return self.end_date > timezone.now()

    @property
    def days_remaining(self):
        if not self.is_active:
            return 0
        remaining = self.end_date - timezone.now()
        return max(0, (remaining.days * 86400 + remaining.seconds + 86399) // 86400)

    def extend_subscription(self, days: int):
        if self.end_date < timezone.now():
            self.end_date = timezone.now()
        self.end_date += timedelta(days=days)
        self.save()

    def __str__(self):
        return f"Подписка для {self.user}"

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
