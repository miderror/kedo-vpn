# backend/content/models.py
from django.db import models


class SiteSettings(models.Model):
    support_link = models.URLField(
        max_length=200,
        verbose_name="Ссылка на поддержку",
        help_text="URL-адрес для кнопки 'Поддержка' в главном меню бота.",
        default="https://t.me/your_support_username",
    )

    def __str__(self):
        return "Тех. поддержка"

    class Meta:
        verbose_name = "Тех. поддержка"
        verbose_name_plural = "Тех. поддержка"
