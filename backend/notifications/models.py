from django.db import models


class NotificationRule(models.Model):
    name = models.CharField(
        max_length=255, verbose_name="Название правила (для админа)"
    )
    trigger_hours_before_expiry = models.PositiveIntegerField(
        verbose_name="Отправить за (часов)",
        help_text="За сколько часов до окончания подписки отправить уведомление.",
    )
    message_template = models.TextField(
        verbose_name="Шаблон сообщения",
        help_text="Используйте {days} для дней и {hours} для часов. Пример: Ваша подписка истекает через {hours} часа(ов)!",
    )
    is_active = models.BooleanField(default=True, verbose_name="Правило активно")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Правило уведомления"
        verbose_name_plural = "Правила уведомлений"
        ordering = ["trigger_hours_before_expiry"]


class SentNotification(models.Model):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    rule = models.ForeignKey(
        NotificationRule, on_delete=models.CASCADE, verbose_name="Правило"
    )
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="Время отправки")
    subscription_end_date_at_send_time = models.DateTimeField(
        verbose_name="Дата окончания подписки в момент отправки"
    )

    def __str__(self):
        return f"Уведомление для {self.user} по правилу '{self.rule.name}'"

    class Meta:
        verbose_name = "Отправленное уведомление"
        verbose_name_plural = "Отправленные уведомления"
        unique_together = ("user", "rule", "subscription_end_date_at_send_time")
