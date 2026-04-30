"""
URL-конфигурация проекта «Читательский дневник».

Маршруты:
    /          — приложение diary (список книг, детали, формы)
    /admin/    — встроенная Django-админка
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("diary.urls")),
]
