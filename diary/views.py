"""
Представления (views) приложения «Читательский дневник».

Маршруты:
    GET  /                  — главная страница со статистикой и списком книг
    GET  /about/            — страница «О дневнике»
    GET  /books/<pk>/       — детальная страница книги
    GET  /books/add/        — форма добавления книги
    POST /books/add/        — сохранение новой книги
    GET  /books/<pk>/edit/  — форма редактирования книги
    POST /books/<pk>/edit/  — сохранение изменений книги
    POST /books/<pk>/delete/ — удаление книги
"""

from django.contrib import messages
from django.db.models import Count, QuerySet, Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BookForm
from .models import Book


# ---------------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------------


def _build_stats(queryset: QuerySet) -> dict:
    """
    Считает статистику по переданному QuerySet книг.

    Возвращает словарь со следующими ключами:
        total_books   — общее число книг
        total_pages   — суммарное число страниц
        books_this_year — книг за текущий год
        pages_this_year — страниц за текущий год
        avg_rating    — средняя оценка (или None)
        current_book  — название последней добавленной книги (или None)
    """
    from datetime import date

    current_year = date.today().year

    aggregated = queryset.aggregate(
        total_books=Count("id"),
        total_pages=Sum("pages"),
    )

    this_year_qs = queryset.filter(year_read=current_year)
    this_year_agg = this_year_qs.aggregate(
        books_this_year=Count("id"),
        pages_this_year=Sum("pages"),
    )

    rated_books = queryset.filter(rating__isnull=False)
    avg_rating: float | None = None
    if rated_books.exists():
        total_rating = sum(b.rating for b in rated_books)
        avg_rating = round(total_rating / rated_books.count(), 1)

    current_book = queryset.order_by("-created_at").values_list("title", flat=True).first()

    return {
        "total_books": aggregated["total_books"] or 0,
        "total_pages": aggregated["total_pages"] or 0,
        "books_this_year": this_year_agg["books_this_year"] or 0,
        "pages_this_year": this_year_agg["pages_this_year"] or 0,
        "avg_rating": avg_rating,
        "current_book": current_book,
    }


# ---------------------------------------------------------------------------
# Основные представления
# ---------------------------------------------------------------------------


def index(request: HttpRequest) -> HttpResponse:
    """
    Главная страница.

    Отображает статистику читательского дневника и последние добавленные книги.
    """
    books = Book.objects.all()
    stats = _build_stats(books)
    return render(
        request,
        "diary/index.html",
        {"books": books, "stats": stats},
    )


def about(request: HttpRequest) -> HttpResponse:
    """Страница «О дневнике» с полным списком книг."""
    books = Book.objects.all()
    return render(request, "diary/about.html", {"books": books})


def book_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Детальная страница отдельной книги."""
    book = get_object_or_404(Book, pk=pk)
    return render(request, "diary/book_detail.html", {"book": book})


# ---------------------------------------------------------------------------
# CRUD: добавление и редактирование
# ---------------------------------------------------------------------------


def book_add(request: HttpRequest) -> HttpResponse:
    """
    Форма добавления новой книги.

    GET  — отображает пустую форму.
    POST — валидирует и сохраняет книгу, затем редиректит на список.
    """
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Книга «{book.title}» успешно добавлена!')
            return redirect("diary:index")
    else:
        form = BookForm()

    return render(request, "diary/book_form.html", {"form": form, "action": "Добавить"})


def book_edit(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Форма редактирования существующей книги.

    GET  — отображает форму с текущими данными.
    POST — валидирует и сохраняет изменения.
    """
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f'Книга «{book.title}» успешно обновлена!')
            return redirect("diary:book_detail", pk=book.pk)
    else:
        form = BookForm(instance=book)

    return render(
        request,
        "diary/book_form.html",
        {"form": form, "book": book, "action": "Сохранить изменения"},
    )


def book_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Удаление книги.

    GET  — страница подтверждения удаления.
    POST — выполняет удаление и редиректит на главную.
    """
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        title = book.title
        book.delete()
        messages.success(request, f'Книга «{title}» удалена.')
        return redirect("diary:index")

    return render(request, "diary/book_confirm_delete.html", {"book": book})
