[![CI](https://github.com/cresta13/reading_dairy_django/actions/workflows/ci.yml/badge.svg)](https://github.com/cresta13/reading_dairy_django/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/cresta13/reading_dairy_django/badge.svg?branch=main)](https://coveralls.io/github/cresta13/reading_dairy_django?branch=main)

# 📖 Читательский дневник — Django
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

# базовые зависимости
pip install -r requirements.txt

# для разработки и тестов
pip install -r requirements/dev.txt
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

### 5. Запустить сервер разработки

```bash
python manage.py runserver
```

Открыть в браузере: **http://127.0.0.1:8000/**

Админка: **http://127.0.0.1:8000/admin/**

### 6. Запустить Redis (нужен Docker или локальная установка)

```bash
# через Docker
docker run -d -p 6379:6379 redis:7

# или если Redis установлен локально
redis-server
```

### 7. Запустить Celery-воркер (в отдельном терминале)

```bash
# Linux / macOS
celery -A reading_diary worker --loglevel=info

# Windows
celery -A reading_diary worker --loglevel=info --pool=solo
```

После этого при добавлении/редактировании/удалении книги
в консоли воркера будут появляться сообщения вида:

```
[ОБНОВЛЕНА] Книга #150 | «Мастер и Маргарита» — Михаил Булгаков1123 | 4800 стр.
```

P.S. добавлено логирование на кастомную команду `seed_books`

---

## Структура проекта

```
reading_dairy_django/                  ← корень проекта Django
├── manage.py                           # точка входа в Django (runserver, migrate и т.д.)
├── db.sqlite3                          # локальная база данных SQLite
├── LICENSE                             # лицензия проекта
├── README.md                           # описание проекта
├── .gitignore                          # игнорируемые git файлы
├── pytest.ini                          # настройки pytest
├── requirements.txt                    # зависимости проекта

├── requirements/
│   ├── base.txt                        # основные зависимости (Django, Celery и т.д.)
│   └── test-or-dev.txt                 # зависимости для разработки и тестирования

├── reading_diary/                      # Django project (конфигурация)
│   ├── __init__.py
│   ├── settings.py                     # настройки Django (DB, Celery, logging и т.д.)
│   ├── urls.py                         # корневые маршруты проекта
│   ├── wsgi.py                         # WSGI для деплоя
│   └── celery.py                       # настройка Celery (Redis broker)

├── diary/                              # основное приложение (бизнес-логика)
│   ├── __init__.py
│   ├── admin.py                        # регистрация моделей в админке
│   ├── apps.py                         # конфигурация приложения diary
│   ├── forms.py                        # Django формы (BookForm)
│   ├── models.py                       # модели (Book)
│   ├── tasks.py                        # Celery задачи (логирование CRUD)
│   ├── urls.py                         # маршруты приложения diary
│   ├── views.py                        # представления (логика страниц)
│   │
│   ├── migrations/                     # миграции базы данных
│   │   ├── __init__.py
│   │   └── 0001_initial.py             # первая миграция (Book model)
│   │
│   ├── management/                     # кастомные Django команды
│   │   └── commands/
│   │       ├── __init__.py
│   │       └── seed_books.py           # заполнение базы тестовыми данными
│   │
│   ├── templates/                      # шаблоны приложения diary
│   │   └── diary/
│   │       ├── index.html              # главная страница (список книг + статистика)
│   │       ├── about.html              # страница "О дневнике"
│   │       ├── book_form.html          # форма создания/редактирования книги
│   │       ├── book_detail.html        # страница книги
│   │       └── book_confirm_delete.html # подтверждение удаления
│   │
│   └── tests/                          # тесты приложения diary (pytest)
│       ├── __init__.py
│       ├── conftest.py                 # фикстуры для тестов
│       ├── test_admin.py               # тесты админки
│       ├── test_commands.py            # тесты management commands
│       ├── test_models.py              # тесты моделей Book
│       ├── test_views.py               # тесты views
│       └── test_tasks_logging.py       # тесты Celery задач логирования

├── templates/
│   └── base.html                       # базовый шаблон (layout сайта)

├── static/
│   └── css/
│       └── diary.css                   # стили проекта
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

## Запуск тестов

```bash
# установить dev-зависимости
pip install -r requirements/dev.txt

# все тесты
pytest -v

# модели
pytest diary/tests/test_models.py -v

# вьюхи  
pytest diary/tests/test_views.py -v

# функции админки
pytest diary/tests/test_admin.py -v

#кастомная команда
pytest diary/tests/test_commands.py -v

#тестирование логирования
pytest diary/tests/test_tasks_logging.py

# один класс
pytest diary/tests/test_models.py::TestBookCreate -v
```
---
