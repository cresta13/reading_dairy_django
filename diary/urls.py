"""
URL-маршруты приложения «Читательский дневник».
"""

from django.urls import path

from . import views

app_name = "diary"

urlpatterns = [
    # Главная страница — статистика + список книг
    path("", views.index, name="index"),
    # Страница «О дневнике»
    path("about/", views.BookListView.as_view(), name="about"),
    # Список всех книг (отдельная страница)
    path("books/", views.BookListView.as_view(), name="book_list"),
    # Добавить новую книгу
    path("books/add/", views.BookCreateView.as_view(), name="book_add"),
    # Детальная страница книги
    path("books/<int:pk>/", views.BookDetailView.as_view(), name="book_detail"),
    # Редактировать книгу
    path("books/<int:pk>/edit/", views.BookUpdateView.as_view(), name="book_edit"),
    # Удалить книгу
    path("books/<int:pk>/delete/", views.BookDeleteView.as_view(), name="book_delete"),
]
