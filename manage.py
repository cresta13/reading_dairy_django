#!/usr/bin/env python
"""Утилита командной строки Django для административных задач."""

import os
import sys


def main() -> None:
    """Точка входа manage.py."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reading_diary.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Не удалось импортировать Django. Убедитесь, что Django установлен "
            "и активирован в виртуальном окружении."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
