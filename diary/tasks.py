"""
Celery-задачи приложения «Читательский дневник».

Каждая задача логирует CRUD-операцию над книгой:
    book_created  — книга добавлена
    book_updated  — книга отредактирована
    book_deleted  — книга удалена

Задачи выполняются асинхронно в фоне — не блокируют HTTP-ответ.
Вывод идёт в консоль воркера (stdout + logging).
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def log_book_created(self, book_id: int, title: str, author: str, pages: int) -> str:
    """
    Логирует добавление новой книги.

    Принимаем примитивные типы (не объект модели) — Celery
    сериализует аргументы в JSON, объекты Django туда не пролезут.
    """
    try:
        message = (
            f"[СОЗДАНА] Книга #{book_id} | "
            f"«{title}» — {author} | "
            f"{pages} стр."
        )
        logger.info(message)
        return message
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)


@shared_task(bind=True, max_retries=3)
def log_book_updated(self, book_id: int, title: str, author: str, pages: int) -> str:
    """Логирует редактирование книги."""
    try:
        message = (
            f"[ОБНОВЛЕНА] Книга #{book_id} | "
            f"«{title}» — {author} | "
            f"{pages} стр."
        )
        logger.info(message)
        return message
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)


@shared_task(bind=True, max_retries=3)
def log_book_deleted(self, book_id: int, title: str, author: str) -> str:
    """
    Логирует удаление книги.

    Книги уже нет в БД к моменту выполнения задачи,
    поэтому передаём данные напрямую, не id для lookup-а.
    """
    try:
        message = f"[УДАЛЕНА] Книга #{book_id} | «{title}» — {author}"
        logger.info(message)
        return message
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)