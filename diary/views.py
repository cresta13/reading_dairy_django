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
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, QuerySet, Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import BookForm
from .models import Book
from .tasks import log_book_created, log_book_deleted, log_book_updated

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

    current_book = (
        queryset.order_by("-created_at").values_list("title", flat=True).first()
    )

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


# ДОБАВИТЬ в конец файла:


class BookListView(ListView):
    """Список всех книг в виде таблицы."""

    model = Book
    template_name = "diary/about.html"
    context_object_name = "books"
    ordering = ["-created_at"]


class BookDetailView(DetailView):
    """Детальная страница книги."""

    model = Book
    template_name = "diary/book_detail.html"
    context_object_name = "book"


class BookCreateView(SuccessMessageMixin, CreateView):
    """Форма добавления новой книги."""

    model = Book
    form_class = BookForm
    template_name = "diary/book_form.html"
    success_url = reverse_lazy("diary:index")
    success_message = "Книга «%(title)s» успешно добавлена!"

    def form_valid(self, form):  # type: ignore[override]
        response = super().form_valid(form)
        book = self.object
        log_book_created.delay(book.pk, book.title, book.author, book.pages)
        return response

    def get_context_data(self, **kwargs: object) -> dict:
        ctx = super().get_context_data(**kwargs)
        ctx["action"] = "Добавить"
        return ctx


class BookUpdateView(SuccessMessageMixin, UpdateView):
    """Форма редактирования существующей книги."""

    model = Book
    form_class = BookForm
    template_name = "diary/book_form.html"
    success_message = "Книга «%(title)s» успешно обновлена!"

    def form_valid(self, form):  # type: ignore[override]
        response = super().form_valid(form)
        book = self.object
        log_book_updated.delay(book.pk, book.title, book.author, book.pages)
        return response

    def get_success_url(self) -> str:
        return reverse_lazy("diary:book_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs: object) -> dict:
        ctx = super().get_context_data(**kwargs)
        ctx["action"] = "Сохранить изменения"
        return ctx


class BookDeleteView(DeleteView):
    """Подтверждение и удаление книги."""

    model = Book
    template_name = "diary/book_confirm_delete.html"
    context_object_name = "book"
    success_url = reverse_lazy("diary:index")

    def form_valid(self, form):  # type: ignore[override]
        book = self.object
        # сохраняем данные до удаления — после super() объекта уже нет
        book_id, title, author = book.pk, book.title, book.author
        messages.success(self.request, f"Книга «{title}» удалена.")
        response = super().form_valid(form)
        log_book_deleted.delay(book_id, title, author)
        return response
