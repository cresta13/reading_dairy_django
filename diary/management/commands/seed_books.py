"""
Кастомная Django-команда для наполнения базы данных тестовыми книгами.

Использование:
    python manage.py seed_books            # добавит книги, если БД пуста
    python manage.py seed_books --force    # очистит и пересоздаст книги
    python manage.py seed_books --count 3  # добавит только 3 книги из набора
"""

from django.core.management.base import BaseCommand, CommandParser

from diary.models import Book
from diary.tasks import log_book_created, log_book_deleted

# ---------------------------------------------------------------------------
# Тестовые данные — те же книги, что были в FastAPI-версии
# ---------------------------------------------------------------------------

SAMPLE_BOOKS: list[dict] = [
    {
        "title": "Анатомия человеческой деструктивности",
        "author": "Эрих Фромм",
        "pages": 320,
        "rating": 4,
        "year_read": 2026,
        "notes": (
            '💬 "Оказывается, у человека гораздо более сильное возбуждение вызывают '
            "гнев, бешенство, жестокость или жажда разрушения, чем любовь, "
            'творчество или другой какой-то продуктивный интерес."'
        ),
    },
    {
        "title": "Похититель душ",
        "author": "Лара Маер",
        "pages": 935,
        "rating": 4,
        "year_read": 2026,
        "notes": '💬 "Ты бессмертна, пока я не решу иначе."',
    },
    {
        "title": "Дзен в искусстве написания книг",
        "author": "Рей Брэдбери",
        "pages": 256,
        "rating": 2,
        "year_read": 2026,
        "notes": (
            '💬 "Нужно опьяняться и насыщаться творчеством, '
            'и реальность не сможет тебя уничтожить."'
        ),
    },
    {
        "title": "Чужестранка",
        "author": "Диана Гэблдон",
        "pages": 1792,
        "rating": 3,
        "year_read": 2026,
        "notes": (
            '💬 "Противостояние толпе требует не просто личного мужества, '
            'оно требует преодоления извечного инстинкта."'
        ),
    },
    {
        "title": "Анджелика в новом свете",
        "author": "Анн и Серж Голон",
        "pages": 720,
        "rating": 5,
        "year_read": 2026,
        "notes": (
            '💬 "Он обнял её, прижал к себе, повторяя, что она не в силах '
            'одной лишь добротой своего сердца спасти мир."'
        ),
    },
    {
        "title": "Мастер и Маргарита",
        "author": "Михаил Булгаков",
        "pages": 480,
        "rating": 5,
        "year_read": 2025,
        "notes": '💬 "Трусость — самый главный порок."',
    },
    {
        "title": "1984",
        "author": "Джордж Оруэлл",
        "pages": 328,
        "rating": 5,
        "year_read": 2025,
        "notes": '💬 "Свобода — это рабство. Незнание — сила."',
    },
    {
        "title": "Сто лет одиночества",
        "author": "Габриэль Гарсия Маркес",
        "pages": 448,
        "rating": 4,
        "year_read": 2024,
        "notes": '💬 "Всё, что он делал, он делал из любви к ней."',
    },
]


class Command(BaseCommand):
    """Наполняет базу данных тестовыми книгами из предустановленного набора."""

    help = "Наполнить базу данных тестовыми книгами"

    def add_arguments(self, parser: CommandParser) -> None:
        """Регистрирует аргументы командной строки."""
        parser.add_argument(
            "--force",
            action="store_true",
            help="Удалить все существующие книги и создать заново.",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=None,
            help="Количество книг для добавления (по умолчанию — все из набора).",
        )

    def handle(self, *args: object, **options: object) -> None:
        """Основная логика команды."""
        force: bool = options["force"]  # type: ignore[assignment]
        count: int | None = options["count"]  # type: ignore[assignment]

        if force:
            # сохраняем данные до удаления
            books_to_delete = list(Book.objects.all().values("id", "title", "author"))
            Book.objects.all().delete()
            for book in books_to_delete:
                log_book_deleted.delay(book["id"], book["title"], book["author"])
            self.stdout.write(
                self.style.WARNING(f"Удалено {len(books_to_delete)} существующих книг.")
            )
        elif Book.objects.exists():
            self.stdout.write(
                self.style.NOTICE(
                    "База уже содержит книги. Используйте --force для пересоздания."
                )
            )
            return

        sample = SAMPLE_BOOKS[:count] if count else SAMPLE_BOOKS
        created_books = [Book(**data) for data in sample]
        Book.objects.bulk_create(created_books)

        # логируем каждую созданную книгу через Celery
        for book in Book.objects.order_by("id").filter(
            title__in=[b["title"] for b in sample]
        ):
            log_book_created.delay(book.pk, book.title, book.author, book.pages)

        self.stdout.write(self.style.SUCCESS(f"✅ Создано {len(created_books)} книг."))
