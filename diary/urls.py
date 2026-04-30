"""
URL-маршруты приложения «Читательский дневник».

Все маршруты подключаются с пространством имён app_name = "diary",
что позволяет использовать {% url 'diary:index' %} в шаблонах.
"""

from django.urls import path

from . import views

app_name = "diary"

urlpatterns = [
    # Главная страница — статистика + список книг
    path("", views.index, name="index"),
    # Страница «О дневнике»
    path("about/", views.about, name="about"),
    # Список всех книг (отдельная страница)
    path("books/", views.about, name="book_list"),
    # Добавить новую книгу
    path("books/add/", views.book_add, name="book_add"),
    # Детальная страница книги
    path("books/<int:pk>/", views.book_detail, name="book_detail"),
    # Редактировать книгу
    path("books/<int:pk>/edit/", views.book_edit, name="book_edit"),
    # Удалить книгу
    path("books/<int:pk>/delete/", views.book_delete, name="book_delete"),
]
