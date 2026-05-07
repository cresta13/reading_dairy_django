"""
Тесты CBV-представлений приложения «Читательский дневник».

Проверяем: HTTP-статусы, корректные шаблоны, CRUD через POST,
редиректы после успешных операций.
"""

from django.urls import reverse

from diary.models import Book

VALID_FORM_DATA = {
    "title": "Тестовая книга",
    "author": "Тест Тестович",
    "pages": 200,
    "rating": 4,
    "year_read": 2024,
    "notes": "Тестовая заметка",
}


class TestIndexView:

    def test_status_ok(self, client, db) -> None:
        response = client.get(reverse("diary:index"))
        assert response.status_code == 200

    def test_uses_correct_template(self, client, db) -> None:
        response = client.get(reverse("diary:index"))
        assert "diary/index.html" in [t.name for t in response.templates]

    def test_stats_in_context(self, client, book) -> None:
        response = client.get(reverse("diary:index"))
        assert "stats" in response.context
        assert response.context["stats"]["total_books"] == 1

    def test_empty_diary_shows_zero(self, client, db) -> None:
        response = client.get(reverse("diary:index"))
        assert response.context["stats"]["total_books"] == 0

    def test_books_in_context(self, client, book) -> None:
        response = client.get(reverse("diary:index"))
        assert book in response.context["books"]


class TestBookListView:

    def test_status_ok(self, client, db) -> None:
        response = client.get(reverse("diary:about"))
        assert response.status_code == 200

    def test_uses_correct_template(self, client, db) -> None:
        response = client.get(reverse("diary:about"))
        assert "diary/about.html" in [t.name for t in response.templates]

    def test_shows_all_books(self, client, book, book_no_rating) -> None:
        response = client.get(reverse("diary:about"))
        assert len(response.context["books"]) == 2

    def test_empty_list(self, client, db) -> None:
        response = client.get(reverse("diary:about"))
        assert len(response.context["books"]) == 0


class TestBookDetailView:

    def test_status_ok(self, client, book) -> None:
        response = client.get(reverse("diary:book_detail", kwargs={"pk": book.pk}))
        assert response.status_code == 200

    def test_404_for_missing_book(self, client, db) -> None:
        response = client.get(reverse("diary:book_detail", kwargs={"pk": 99999}))
        assert response.status_code == 404

    def test_uses_correct_template(self, client, book) -> None:
        response = client.get(reverse("diary:book_detail", kwargs={"pk": book.pk}))
        assert "diary/book_detail.html" in [t.name for t in response.templates]

    def test_book_in_context(self, client, book) -> None:
        response = client.get(reverse("diary:book_detail", kwargs={"pk": book.pk}))
        assert response.context["book"] == book

    def test_title_in_response(self, client, book) -> None:
        response = client.get(reverse("diary:book_detail", kwargs={"pk": book.pk}))
        assert book.title.encode() in response.content


class TestBookCreateView:

    def test_get_status_ok(self, client, db) -> None:
        response = client.get(reverse("diary:book_add"))
        assert response.status_code == 200

    def test_uses_correct_template(self, client, db) -> None:
        response = client.get(reverse("diary:book_add"))
        assert "diary/book_form.html" in [t.name for t in response.templates]

    def test_create_book_redirects(self, client, db) -> None:
        response = client.post(reverse("diary:book_add"), data=VALID_FORM_DATA)
        assert response.status_code == 302

    def test_create_book_saves_to_db(self, client, db) -> None:
        client.post(reverse("diary:book_add"), data=VALID_FORM_DATA)
        assert Book.objects.filter(title="Тестовая книга").exists()

    def test_invalid_form_no_title(self, client, db) -> None:
        """Форма без обязательного поля возвращает страницу с ошибкой."""
        data = {**VALID_FORM_DATA, "title": ""}
        response = client.post(reverse("diary:book_add"), data=data)
        assert response.status_code == 200  # форма вернулась, не редирект
        assert Book.objects.count() == 0


class TestBookUpdateView:

    def test_get_status_ok(self, client, book) -> None:
        response = client.get(reverse("diary:book_edit", kwargs={"pk": book.pk}))
        assert response.status_code == 200

    def test_404_for_missing_book(self, client, db) -> None:
        response = client.get(reverse("diary:book_edit", kwargs={"pk": 99999}))
        assert response.status_code == 404

    def test_update_redirects_to_detail(self, client, book) -> None:
        response = client.post(
            reverse("diary:book_edit", kwargs={"pk": book.pk}),
            data={**VALID_FORM_DATA, "title": "Обновлённая"},
        )
        assert response.status_code == 302
        assert f"/books/{book.pk}/" in response["Location"]

    def test_update_changes_db(self, client, book) -> None:
        client.post(
            reverse("diary:book_edit", kwargs={"pk": book.pk}),
            data={**VALID_FORM_DATA, "title": "Новое название"},
        )
        book.refresh_from_db()
        assert book.title == "Новое название"

    def test_form_prepopulated(self, client, book) -> None:
        """Форма редактирования содержит текущие данные книги."""
        response = client.get(reverse("diary:book_edit", kwargs={"pk": book.pk}))
        assert book.title.encode() in response.content


class TestBookDeleteView:

    def test_get_confirmation_page(self, client, book) -> None:
        response = client.get(reverse("diary:book_delete", kwargs={"pk": book.pk}))
        assert response.status_code == 200

    def test_uses_correct_template(self, client, book) -> None:
        response = client.get(reverse("diary:book_delete", kwargs={"pk": book.pk}))
        assert "diary/book_confirm_delete.html" in [t.name for t in response.templates]

    def test_post_deletes_book(self, client, book) -> None:
        pk = book.pk
        client.post(reverse("diary:book_delete", kwargs={"pk": book.pk}))
        assert not Book.objects.filter(pk=pk).exists()

    def test_post_redirects_to_index(self, client, book) -> None:
        response = client.post(reverse("diary:book_delete", kwargs={"pk": book.pk}))
        assert response.status_code == 302
        assert response["Location"] == reverse("diary:index")

    def test_404_for_missing_book(self, client, db) -> None:
        response = client.post(reverse("diary:book_delete", kwargs={"pk": 99999}))
        assert response.status_code == 404
