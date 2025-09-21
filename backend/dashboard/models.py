from backend.users.models import User


class ProjectStats(User):
    class Meta:
        proxy = True
        verbose_name = "Статистика Проекта"
        verbose_name_plural = "Статистика Проекта"
