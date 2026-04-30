"""Конфигурация приложения diary."""

from django.apps import AppConfig


class DiaryConfig(AppConfig):
    """Приложение «Читательский дневник»."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "diary"
    verbose_name = "Читательский дневник"
