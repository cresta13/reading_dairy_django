"""
Тесты кастомных действий Django-админки.

Проверяем два action-а:
    show_reading_stats — выводит статистику по выбранным книгам
    set_rating_five    — ставит оценку 5 выбранным книгам
"""

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory

from diary.admin import BookAdmin, set_rating_five, show_reading_stats
from diary.models import Book


@pytest.fixture
def admin_request(db):
    """Фейковый request с поддержкой messages — нужен для action-ов."""
    factory = RequestFactory()
    request = factory.get("/admin/diary/book/")
    # Django messages требует session и _messages на реквесте
    request.session = {}
    request._messages = FallbackStorage(request)
    return request


@pytest.fixture
def model_admin():
    """Экземпляр BookAdmin — нужен чтобы вызывать action-ы напрямую."""
    return BookAdmin(model=Book, admin_site=AdminSite())


@pytest.fixture
def three_books(db) -> list[Book]:
    """Три книги с разными рейтингами для проверки статистики."""
    return [
        Book.objects.create(
            title="Книга 1", author="Автор", pages=100, rating=2, year_read=2024
        ),
        Book.objects.create(
            title="Книга 2", author="Автор", pages=200, rating=4, year_read=2024
        ),
        Book.objects.create(title="Книга 3", author="Автор", pages=300),  # без рейтинга
    ]


# ---------------------------------------------------------------------------
# show_reading_stats
# ---------------------------------------------------------------------------


class TestShowReadingStats:

    def test_message_contains_book_count(
        self, model_admin, admin_request, three_books
    ) -> None:
        """Сообщение содержит количество выбранных книг."""
        queryset = Book.objects.all()
        show_reading_stats(model_admin, admin_request, queryset)
        messages = list(get_messages(admin_request))
        assert len(messages) == 1
        assert "3" in messages[0].message

    def test_message_contains_total_pages(
        self, model_admin, admin_request, three_books
    ) -> None:
        """Сообщение содержит суммарное число страниц."""
        queryset = Book.objects.all()
        show_reading_stats(model_admin, admin_request, queryset)
        messages = list(get_messages(admin_request))
        # 100 + 200 + 300 = 600
        assert "600" in messages[0].message

    def test_message_contains_avg_rating(
        self, model_admin, admin_request, three_books
    ) -> None:
        """Сообщение содержит среднюю оценку только по книгам с рейтингом."""
        queryset = Book.objects.all()
        show_reading_stats(model_admin, admin_request, queryset)
        messages = list(get_messages(admin_request))
        # (2 + 4) / 2 = 3.0
        assert "3.0" in messages[0].message

    def test_message_no_rated_books(self, model_admin, admin_request, db) -> None:
        """Если ни у одной книги нет рейтинга — показывает 'не указана'."""
        Book.objects.create(title="Без оценки", author="А", pages=50)
        queryset = Book.objects.all()
        show_reading_stats(model_admin, admin_request, queryset)
        messages = list(get_messages(admin_request))
        assert "не указана" in messages[0].message

    def test_empty_queryset(self, model_admin, admin_request, db) -> None:
        """Пустой queryset — показывает нули, не падает."""
        queryset = Book.objects.none()
        show_reading_stats(model_admin, admin_request, queryset)
        messages = list(get_messages(admin_request))
        assert "0" in messages[0].message


# ---------------------------------------------------------------------------
# set_rating_five
# ---------------------------------------------------------------------------


class TestSetRatingFive:

    def test_updates_all_selected(
        self, model_admin, admin_request, three_books
    ) -> None:
        """Всем выбранным книгам выставляется рейтинг 5."""
        queryset = Book.objects.all()
        set_rating_five(model_admin, admin_request, queryset)
        assert Book.objects.filter(rating=5).count() == 3

    def test_updates_only_selected(
        self, model_admin, admin_request, three_books
    ) -> None:
        """Книги вне queryset не затрагиваются."""
        untouched = Book.objects.create(
            title="Не трогать", author="А", pages=10, rating=1
        )
        queryset = Book.objects.filter(pk__in=[b.pk for b in three_books])
        set_rating_five(model_admin, admin_request, queryset)
        untouched.refresh_from_db()
        assert untouched.rating == 1

    def test_success_message_contains_count(
        self, model_admin, admin_request, three_books
    ) -> None:
        """Сообщение об успехе содержит количество обновлённых книг."""
        queryset = Book.objects.all()
        set_rating_five(model_admin, admin_request, queryset)
        messages = list(get_messages(admin_request))
        assert "3" in messages[0].message

    def test_overwrites_existing_rating(self, model_admin, admin_request, db) -> None:
        """Существующий рейтинг перезаписывается."""
        book = Book.objects.create(title="Т", author="А", pages=1, rating=2)
        set_rating_five(model_admin, admin_request, Book.objects.all())
        book.refresh_from_db()
        assert book.rating == 5
