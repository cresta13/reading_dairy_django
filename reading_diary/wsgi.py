"""WSGI-точка входа для production-серверов (gunicorn, uWSGI и т.п.)."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reading_diary.settings")

application = get_wsgi_application()
