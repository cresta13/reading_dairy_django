# Инициализируем Celery при старте Django
from .celery import app as celery_app  # noqa: F401

__all__ = ["celery_app"]
# reading_diary package
