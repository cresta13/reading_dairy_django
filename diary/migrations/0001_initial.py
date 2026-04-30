"""Начальная миграция — создание таблицы Book."""

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies: list = []

    operations = [
        migrations.CreateModel(
            name="Book",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=300, verbose_name="Название")),
                ("author", models.CharField(max_length=200, verbose_name="Автор")),
                (
                    "pages",
                    models.PositiveIntegerField(verbose_name="Количество страниц"),
                ),
                (
                    "rating",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Оценка (1–5)",
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(5),
                        ],
                    ),
                ),
                (
                    "year_read",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Год прочтения",
                        validators=[
                            django.core.validators.MinValueValidator(1900),
                            django.core.validators.MaxValueValidator(2100),
                        ],
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        blank=True, null=True, verbose_name="Заметки / цитата"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата добавления"
                    ),
                ),
            ],
            options={
                "verbose_name": "Книга",
                "verbose_name_plural": "Книги",
                "ordering": ["-created_at"],
            },
        ),
    ]
