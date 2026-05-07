"""
Тесты кастомной команды seed_books.

Проверяем: базовый запуск, флаг --force, флаг --count,
поведение при непустой БД.
"""

from django.core.management import call_command

from diary.models import Book


class TestSeedBooksCommand:

    def test_creates_books_in_empty_db(self, db) -> None:
        """Команда создаёт книги если БД пустая."""
        call_command("seed_books")
        assert Book.objects.count() > 0

    def test_does_not_run_if_db_not_empty(self, db) -> None:
        """Если книги уже есть — команда без --force ничего не делает."""
        Book.objects.create(title="Существующая", author="А", pages=1)
        call_command("seed_books")
        # должна остаться ровно одна книга — та что была
        assert Book.objects.count() == 1

    def test_force_clears_existing_books(self, db) -> None:
        """Флаг --force удаляет старые книги перед созданием новых."""
        Book.objects.create(title="Старая", author="А", pages=1)
        call_command("seed_books", force=True)
        # старой книги быть не должно
        assert not Book.objects.filter(title="Старая").exists()

    def test_force_creates_fresh_books(self, db) -> None:
        """После --force в БД есть книги из тестового набора."""
        Book.objects.create(title="Старая", author="А", pages=1)
        call_command("seed_books", force=True)
        assert Book.objects.count() > 0

    def test_count_limits_created_books(self, db) -> None:
        """Флаг --count ограничивает количество созданных книг."""
        call_command("seed_books", count=3)
        assert Book.objects.count() == 3

    def test_count_one(self, db) -> None:
        """--count 1 создаёт ровно одну книгу."""
        call_command("seed_books", count=1)
        assert Book.objects.count() == 1

    def test_created_books_have_required_fields(self, db) -> None:
        """Все созданные книги имеют title, author и pages."""
        call_command("seed_books")
        for book in Book.objects.all():
            assert book.title
            assert book.author
            assert book.pages > 0

    def test_idempotent_with_force(self, db) -> None:
        """Двойной запуск с --force даёт одинаковый результат."""
        call_command("seed_books", force=True)
        count_first = Book.objects.count()
        call_command("seed_books", force=True)
        count_second = Book.objects.count()
        assert count_first == count_second
