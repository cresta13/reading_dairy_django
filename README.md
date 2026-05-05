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
├── db.sqlite3
├── LICENSE
├── README.md
├── .gitignore
├── pytest.ini
├── requirements.txt
├── requirements/
│   ├── base.txt              # Основные зависимости проекта
│   └── test-or-dev.txt       # Зависимости для разработки и тестов
│
├── reading_diary/            # Настройки Django
│   ├── __init__.py
│   ├── settings.py           # Основные настройки проекта
│   ├── urls.py               # Корневые маршруты
│   └── wsgi.py               # WSGI-конфигурация для деплоя
│
├── diary/                    # Основное приложение
│   ├── __init__.py
│   ├── admin.py              # Настройка админ-панели
│   ├── apps.py               # Конфигурация приложения
│   ├── forms.py              # Django формы (BookForm)
│   ├── models.py             # Модели данных (Book)
│   ├── urls.py               # URL-маршруты приложения
│   ├── views.py              # Представления (логика)
│   │
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py   # Первая миграция (создание моделей)
│   │
│   ├── management/
│   │   └── commands/
│   │       ├── __init__.py
│   │       └── seed_books.py # Кастомная команда заполнения БД
│   │
│   └── templates/
│       └── diary/
│           ├── about.html                # Страница со списком книг
│           ├── book_confirm_delete.html # Подтверждение удаления
│           ├── book_detail.html         # Детальная страница книги
│           ├── book_form.html           # Форма создания/редактирования
│           └── index.html               # Главная страница
│
├── templates/
│   └── base.html            # Базовый шаблон (layout, navbar)
│
├── static/
│   └── css/
│       └── diary.css        # Кастомные стили проекта
│
└── tests/
    ├── __init__.py
    ├── conftest.py          # Общие фикстуры для тестов
    ├── test_admin.py        # Тесты админки
    ├── test_commands.py     # Тесты management-команд
    ├── test_models.py       # Тесты моделей
    └── test_views.py        # Тесты представлений
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
pytest tests/test_models.py -v

# вьюхи  
pytest tests/test_views.py -v

# функции админки
pytest tests/test_admin.py -v

#кастомная команда
pytest tests/test_commands.py -v

# один класс
pytest tests/test_models.py::TestBookCreate -v
```
---
