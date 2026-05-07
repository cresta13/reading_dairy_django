"""
Тесты Celery-задач читательского дневника.

Используем eager-режим (CELERY_TASK_ALWAYS_EAGER=True) —
задачи выполняются синхронно прямо в тесте, Redis не нужен.
"""

from unittest.mock import patch

import pytest

from diary.tasks import log_book_created, log_book_deleted, log_book_updated


@pytest.fixture(autouse=True)
def celery_eager(settings):
    """Выполнять задачи синхронно — без реального воркера и Redis."""
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True


class TestLogBookCreatedTask:
    """Тесты задачи логирования создания книги."""

    def test_returns_message(self) -> None:
        """Задача возвращает сообщение с данными книги."""
        result = log_book_created.delay(1, "1984", "Оруэлл", 328)

        message = result.get()

        assert "1984" in message
        assert "Оруэлл" in message
        assert "328" in message

    def test_message_contains_created_marker(self) -> None:
        """Сообщение содержит маркер создания."""
        result = log_book_created.delay(42, "Тест", "Автор", 100)

        assert "СОЗДАНА" in result.get()

    def test_logs_via_logger(self) -> None:
        """Задача пишет сообщение в logger.info."""
        with patch("diary.tasks.logger") as mock_logger:
            log_book_created.delay(1, "Тест", "Автор", 100)

            mock_logger.info.assert_called_once()


class TestLogBookUpdatedTask:
    """Тесты задачи логирования обновления книги."""

    def test_returns_message(self) -> None:
        result = log_book_updated.delay(
            1,
            "Обновлённая книга",
            "Автор",
            200,
        )

        message = result.get()

        assert "Обновлённая книга" in message
        assert "200" in message

    def test_message_contains_updated_marker(self) -> None:
        """Сообщение содержит маркер обновления."""
        result = log_book_updated.delay(1, "Тест", "Автор", 100)

        assert "ОБНОВЛЕНА" in result.get()

    def test_logs_via_logger(self) -> None:
        with patch("diary.tasks.logger") as mock_logger:
            log_book_updated.delay(1, "Тест", "Автор", 100)

            mock_logger.info.assert_called_once()


class TestLogBookDeletedTask:
    """Тесты задачи логирования удаления книги."""

    def test_returns_message(self) -> None:
        result = log_book_deleted.delay(1, "Удалённая книга", "Автор")

        message = result.get()

        assert "Удалённая книга" in message
        assert "Автор" in message

    def test_message_contains_deleted_marker(self) -> None:
        """Сообщение содержит маркер удаления."""
        result = log_book_deleted.delay(1, "Тест", "Автор")

        assert "УДАЛЕНА" in result.get()

    def test_logs_via_logger(self) -> None:
        with patch("diary.tasks.logger") as mock_logger:
            log_book_deleted.delay(1, "Тест", "Автор")

            mock_logger.info.assert_called_once()

    def test_deleted_task_does_not_require_pages(self) -> None:
        """Удалённая книга не требует pages в сигнатуре."""
        result = log_book_deleted.delay(99, "Книга", "Автор")

        assert result.get() is not None
