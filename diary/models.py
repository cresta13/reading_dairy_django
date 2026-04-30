"""
Модели приложения «Читательский дневник».

Основная сущность — Book (книга с оценкой, годом прочтения и заметками).
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Book(models.Model):
    """Запись о прочитанной книге в читательском дневнике."""

    title: str = models.CharField(
        max_length=300,
        verbose_name="Название",
    )
    author: str = models.CharField(
        max_length=200,
        verbose_name="Автор",
    )
    pages: int = models.PositiveIntegerField(
        verbose_name="Количество страниц",
    )
    rating: int | None = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Оценка (1–5)",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    year_read: int | None = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Год прочтения",
        validators=[MinValueValidator(1900), MaxValueValidator(2100)],
    )
    notes: str | None = models.TextField(
        null=True,
        blank=True,
        verbose_name="Заметки / цитата",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления",
    )

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} — {self.author}"

    def stars_display(self) -> str:
        """Возвращает строку со звёздочками для отображения рейтинга."""
        if self.rating is None:
            return "—"
        return "★" * self.rating + "☆" * (5 - self.rating)
