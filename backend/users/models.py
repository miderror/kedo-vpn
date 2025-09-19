from django.db import models


class User(models.Model):
    telegram_id = models.BigIntegerField(
        unique=True, primary_key=True, verbose_name="Телеграм ID"
    )
    username = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Юзернейм"
    )

    referred_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referrals",
        verbose_name="Кто пригласил",
    )

    date_joined = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата регистрации"
    )

    def __str__(self):
        return f"id: {str(self.telegram_id)}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
