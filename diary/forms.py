"""
Формы приложения «Читательский дневник».

BookForm используется как для создания, так и для редактирования книги.
"""

from django import forms

from .models import Book

RATING_CHOICES = [
    ("", "— не указано —"),
    (1, "★☆☆☆☆  (1 — разочарование)"),
    (2, "★★☆☆☆  (2 — слабо)"),
    (3, "★★★☆☆  (3 — нормально)"),
    (4, "★★★★☆  (4 — хорошо)"),
    (5, "★★★★★  (5 — шедевр)"),
]


class BookForm(forms.ModelForm):
    """Форма добавления и редактирования книги."""

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        required=False,
        label="Оценка",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Book
        fields = ["title", "author", "pages", "rating", "year_read", "notes"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Название книги"}
            ),
            "author": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Имя автора"}
            ),
            "pages": forms.NumberInput(
                attrs={"class": "form-control", "min": 1}
            ),
            "year_read": forms.NumberInput(
                attrs={"class": "form-control", "min": 1900, "max": 2100}
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Цитата или личные впечатления…",
                }
            ),
        }
        labels = {
            "title": "Название",
            "author": "Автор",
            "pages": "Страниц",
            "year_read": "Год прочтения",
            "notes": "Заметки / цитата",
        }

    def clean_rating(self) -> int | None:
        """Преобразует строковое значение рейтинга в int или None."""
        value = self.cleaned_data.get("rating")
        if value == "" or value is None:
            return None
        return int(value)

    def clean_pages(self) -> int:
        """Проверяет, что количество страниц положительное."""
        pages = self.cleaned_data.get("pages")
        if pages is not None and pages <= 0:
            raise forms.ValidationError("Количество страниц должно быть больше нуля.")
        return pages
