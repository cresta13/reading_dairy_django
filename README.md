# 📖 Читательский дневник

Веб-приложение для ведения личного читательского дневника.

## Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone https://github.com/cresta13/reading_dairy_django
```

### 2. Создать виртуальное окружение и установить зависимости

```bash
python -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 3. Выполнить миграции

```bash
python manage.py migrate
```

### 4. Для проверки админки

#### 4.1 Создать своего суперпользователя
```bash
python manage.py createsuperuser
```

или

#### 4.2 Использовать готового

логин: maxzero

пароль: maxmaxmax

### 6. Запустить сервер разработки

```bash
python manage.py runserver
```

Открыть в браузере: **http://127.0.0.1:8000/**

Админка: **http://127.0.0.1:8000/admin/**

---

## Структура проекта

```
reading_diary/                  ← корень проекта
├── manage.py
├── requirements.txt
├── db.sqlite3                  ← БД
│
├── reading_diary/              ← пакет настроек Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── diary/                      ← основное приложение
│   ├── models.py               ← модель Book
│   ├── views.py                ← все представления
│   ├── forms.py                ← BookForm (добавление/редактирование)
│   ├── urls.py                 ← маршруты приложения
│   ├── admin.py                ← кастомная настройка админки
│   ├── apps.py
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── management/
│   │   └── commands/
│   │       └── seed_books.py   ← кастомная команда
│   └── templates/
│       └── diary/
│           ├── index.html          ← главная страница
│           ├── about.html          ← список всех книг (таблица)
│           ├── book_detail.html    ← страница книги
│           ├── book_form.html      ← форма добавления / редактирования
│           └── book_confirm_delete.html
│
├── templates/
│   └── base.html               ← базовый шаблон (navbar, footer, messages)
│
└── static/
    └── css/
        └── diary.css           ← кастомные стили
```

---

## Маршруты

| URL                        | Метод    | Описание                          |
|----------------------------|----------|-----------------------------------|
| `/`                        | GET      | Главная: статистика + карточки книг |
| `/about/`                  | GET      | Таблица всех книг                 |
| `/books/add/`              | GET/POST | Форма добавления книги            |
| `/books/<pk>/`             | GET      | Детальная страница книги          |
| `/books/<pk>/edit/`        | GET/POST | Форма редактирования книги        |
| `/books/<pk>/delete/`      | GET/POST | Подтверждение удаления            |
| `/admin/`                  | —        | Django-админка                    |

---

## Модель Book

| Поле         | Тип                  | Описание                      |
|--------------|----------------------|-------------------------------|
| `id`         | BigAutoField         | Первичный ключ                |
| `title`      | CharField(300)       | Название книги                |
| `author`     | CharField(200)       | Автор                         |
| `pages`      | PositiveIntegerField | Количество страниц            |
| `rating`     | PositiveSmallIntegerField (1–5) | Оценка (опционально) |
| `year_read`  | PositiveSmallIntegerField | Год прочтения (опционально) |
| `notes`      | TextField            | Заметки / цитата (опционально)|
| `created_at` | DateTimeField        | Дата добавления (auto)        |

---

## Кастомная команда `seed_books`

```bash
# Показать справку
python manage.py seed_books --help

# Добавить тестовые книги (только если БД пуста)
python manage.py seed_books

# Очистить БД и добавить заново
python manage.py seed_books --force

# Добавить только 3 книги
python manage.py seed_books --count 3
```

---

## Настройка админки

Модель `Book` зарегистрирована с расширенными возможностями:

- **`list_display`** — столбцы: название, автор, страницы, оценка (звёздочки), год, дата добавления
- **`list_filter`** — фильтр по оценке и году прочтения
- **`search_fields`** — поиск по названию, автору, заметкам
- **`@admin.action`** — два действия:
  - 📊 **Показать статистику** — считает количество книг, суммарные страницы и среднюю оценку
  - ⭐ **Поставить оценку 5** — массово устанавливает максимальный рейтинг

---
