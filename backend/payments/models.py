from django.db import models


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Ожидает"
        SUCCEEDED = "SUCCEEDED", "Успешно"
        CANCELED = "CANCELED", "Отменен"

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Пользователь",
    )
    tariff = models.ForeignKey(
        "vpn.Tariff", on_delete=models.PROTECT, verbose_name="Тариф"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    payment_id_provider = models.CharField(
        max_length=255, unique=True, verbose_name="ID платежа в ЮKassa"
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Статус",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return f"Платеж {self.id} от {self.user} на {self.amount}₽"

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-created_at"]
