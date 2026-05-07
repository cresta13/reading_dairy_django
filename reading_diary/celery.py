"""
Настройка Celery для проекта «Читательский дневник».

Redis используется как брокер задач и бэкенд хранения результатов.
"""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reading_diary.settings")

app = Celery("reading_diary")

# Берём конфиг из Django settings, ищем переменные с префиксом CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматически находим tasks.py во всех INSTALLED_APPS
app.autodiscover_tasks()