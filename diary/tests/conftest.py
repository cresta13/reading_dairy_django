"""Общие фикстуры для всех тестов."""

import pytest

from diary.models import Book


@pytest.fixture
def book(db) -> Book:
    """Одна книга со всеми полями — используется в большинстве тестов."""
    return Book.objects.create(
        title="Мастер и Маргарита",
        author="Михаил Булгаков",
        pages=480,
        rating=5,
        year_read=2024,
        notes="Трусость — самый главный порок.",
    )


@pytest.fixture
def book_no_rating(db) -> Book:
    """Книга без оценки и года — проверяем опциональные поля."""
    return Book.objects.create(
        title="Незнайка на Луне",
        author="Николай Носов",
        pages=320,
    )
