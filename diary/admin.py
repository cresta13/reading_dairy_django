"""
Настройка Django-админки для приложения «Читательский дневник».

Кастомизации:
    - list_display   — столбцы в таблице списка книг
    - list_filter    — панель фильтров справа
    - search_fields  — полнотекстовый поиск
    - @admin.action  — кастомное действие «Статистика выбранных книг»
"""

from django.contrib import admin
from django.db.models import QuerySet, Sum
from django.http import HttpRequest

from .models import Book


# ---------------------------------------------------------------------------
# Кастомные действия
# ---------------------------------------------------------------------------


@admin.action(description="📊 Показать статистику прочитанных книг")
def show_reading_stats(
    modeladmin: "BookAdmin",
    request: HttpRequest,
    queryset: QuerySet[Book],
) -> None:
    """
    Считает суммарную статистику по выбранным книгам и выводит
    её в виде info-сообщения в шапке страницы.

    Статистика включает: количество книг, суммарное число страниц,
    среднюю оценку.
    """
    total_books = queryset.count()
    total_pages = queryset.aggregate(total=Sum("pages"))["total"] or 0

    rated = queryset.filter(rating__isnull=False)
    if rated.exists():
        avg_rating = sum(b.rating for b in rated) / rated.count()
        avg_str = f"{avg_rating:.1f} ★"
    else:
        avg_str = "не указана"

    modeladmin.message_user(
        request,
        (
            f"📚 Выбрано книг: {total_books} | "
            f"📄 Суммарно страниц: {total_pages:,} | "
            f"⭐ Средняя оценка: {avg_str}"
        ),
    )


@admin.action(description="⭐ Поставить оценку 5 выбранным книгам")
def set_rating_five(
    modeladmin: "BookAdmin",
    request: HttpRequest,
    queryset: QuerySet[Book],
) -> None:
    """Устанавливает максимальную оценку (5) для выбранных книг."""
    updated = queryset.update(rating=5)
    modeladmin.message_user(request, f"Оценка 5 ★ установлена для {updated} книг.")


# ---------------------------------------------------------------------------
# Регистрация модели
# ---------------------------------------------------------------------------


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Настройка отображения модели Book в Django-админке."""

    # Столбцы в списке книг
    list_display = (
        "title",
        "author",
        "pages",
        "stars_display",
        "year_read",
        "created_at",
    )

    # Фильтры в правой панели
    list_filter = ("rating", "year_read")

    # Поля для поиска (через LIKE %...%)
    search_fields = ("title", "author", "notes")

    # Поля только для чтения в форме редактирования
    readonly_fields = ("created_at",)

    # Порядок полей в форме
    fields = ("title", "author", "pages", "rating", "year_read", "notes", "created_at")

    # Кастомные действия
    actions = [show_reading_stats, set_rating_five]

    # Количество записей на странице
    list_per_page = 20

    @admin.display(description="Оценка")
    def stars_display(self, obj: Book) -> str:
        """Отображает рейтинг книги в виде звёздочек."""
        return obj.stars_display()
