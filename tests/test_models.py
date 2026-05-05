"""
Тесты модели Book.

Покрываем: создание, чтение, обновление, удаление (CRUD),
валидаторы полей и вспомогательный метод stars_display().
"""

import pytest
from django.core.exceptions import ValidationError

from diary.models import Book


class TestBookCreate:
    """Создание записей."""

    def test_create_full(self, db) -> None:
        """Книга со всеми полями сохраняется корректно."""
        book = Book.objects.create(
            title="1984",
            author="Джордж Оруэлл",
            pages=328,
            rating=5,
            year_read=2023,
            notes="Свобода — это рабство.",
        )
        assert book.pk is not None
        assert book.title == "1984"
        assert book.pages == 328
        assert book.rating == 5

    def test_create_minimal(self, db) -> None:
        """Книга только с обязательными полями сохраняется."""
        book = Book.objects.create(
            title="Без оценки",
            author="Аноним",
            pages=100,
        )
        assert book.pk is not None
        assert book.rating is None
        assert book.year_read is None
        assert book.notes is None

    def test_created_at_auto(self, db) -> None:
        """Поле created_at заполняется автоматически."""
        book = Book.objects.create(title="Тест", author="Тест", pages=1)
        assert book.created_at is not None

    def test_str_representation(self, book: Book) -> None:
        """__str__ возвращает 'Название — Автор'."""
        assert str(book) == "Мастер и Маргарита — Михаил Булгаков"

    def test_default_ordering(self, db) -> None:
        """Книги сортируются по убыванию даты добавления."""
        b1 = Book.objects.create(title="Первая", author="А", pages=100)
        b2 = Book.objects.create(title="Вторая", author="Б", pages=200)
        books = list(Book.objects.all())
        assert books[0].pk == b2.pk
        assert books[1].pk == b1.pk


class TestBookRead:
    """Чтение записей."""

    def test_get_by_pk(self, book: Book) -> None:
        """Можно получить книгу по первичному ключу."""
        fetched = Book.objects.get(pk=book.pk)
        assert fetched.title == book.title

    def test_filter_by_rating(self, book: Book, book_no_rating: Book) -> None:
        """Фильтрация по наличию рейтинга работает корректно."""
        rated = Book.objects.filter(rating__isnull=False)
        unrated = Book.objects.filter(rating__isnull=True)
        assert book in rated
        assert book_no_rating in unrated

    def test_filter_by_year(self, book: Book, db) -> None:
        """Фильтрация по году прочтения работает."""
        Book.objects.create(title="Другая", author="Ктото", pages=50, year_read=2020)
        assert Book.objects.filter(year_read=2024).count() == 1
        assert Book.objects.filter(year_read=2020).count() == 1

    def test_count(self, book: Book, book_no_rating: Book) -> None:
        """Счётчик записей работает правильно."""
        assert Book.objects.count() == 2


class TestBookUpdate:
    """Обновление записей."""

    def test_update_title(self, book: Book) -> None:
        """Обновление названия через save() сохраняется в БД."""
        book.title = "Белая гвардия"
        book.save()
        assert Book.objects.get(pk=book.pk).title == "Белая гвардия"

    def test_update_rating(self, book: Book) -> None:
        """Рейтинг можно обновить."""
        book.rating = 3
        book.save()
        assert Book.objects.get(pk=book.pk).rating == 3

    def test_bulk_update(self, db) -> None:
        """queryset.update() применяется ко всем записям."""
        Book.objects.create(title="А", author="А", pages=10)
        Book.objects.create(title="Б", author="Б", pages=20)
        Book.objects.all().update(year_read=2025)
        assert Book.objects.filter(year_read=2025).count() == 2

    def test_set_optional_to_none(self, book: Book) -> None:
        """Можно обнулить опциональные поля."""
        book.rating = None
        book.notes = None
        book.save()
        refreshed = Book.objects.get(pk=book.pk)
        assert refreshed.rating is None
        assert refreshed.notes is None


class TestBookDelete:
    """Удаление записей."""

    def test_delete_single(self, book: Book) -> None:
        """Удаление одной записи уменьшает счётчик."""
        pk = book.pk
        book.delete()
        assert not Book.objects.filter(pk=pk).exists()

    def test_delete_all(self, book: Book, book_no_rating: Book) -> None:
        """queryset.delete() удаляет все записи."""
        Book.objects.all().delete()
        assert Book.objects.count() == 0

    def test_delete_nonexistent_raises(self, db) -> None:
        """Обращение к несуществующей записи вызывает исключение."""
        with pytest.raises(Book.DoesNotExist):
            Book.objects.get(pk=99999)


class TestBookValidation:
    """Валидаторы полей модели."""

    def test_rating_above_max_fails(self, db) -> None:
        """Рейтинг больше 5 не проходит валидацию."""
        book = Book(title="Т", author="А", pages=1, rating=6)
        with pytest.raises(ValidationError):
            book.full_clean()

    def test_rating_below_min_fails(self, db) -> None:
        """Рейтинг меньше 1 не проходит валидацию."""
        book = Book(title="Т", author="А", pages=1, rating=0)
        with pytest.raises(ValidationError):
            book.full_clean()

    def test_rating_boundary_values(self, db) -> None:
        """Граничные значения рейтинга 1 и 5 допустимы."""
        for rating in (1, 5):
            book = Book(title="Т", author="А", pages=1, rating=rating)
            book.full_clean()  # не должно бросать исключение


class TestStarsDisplay:
    """Метод stars_display()."""

    def test_five_stars(self, book: Book) -> None:
        assert book.stars_display() == "★★★★★"

    def test_three_stars(self, db) -> None:
        book = Book.objects.create(title="Т", author="А", pages=1, rating=3)
        assert book.stars_display() == "★★★☆☆"

    def test_no_rating(self, book_no_rating: Book) -> None:
        assert book_no_rating.stars_display() == "—"
