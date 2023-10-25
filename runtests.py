import sys

from os.path import abspath, dirname, join
from shutil import rmtree

import pytest

from django.conf import settings


sys.path.insert(0, abspath(dirname(__file__)))


media_root = join(abspath(dirname(__file__)), "test_files")
rmtree(media_root, ignore_errors=True)

installed_apps = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.admin",
    "django.contrib.postgres",
    "pycaption",
    "tests",
]

DEFAULT_SETTINGS = dict(
    SECRET_KEY='test_m90nvn4y^n4tya6u1slk24u*)+7@qg-t8qg9^-v7=36!62*gki',
    MEDIA_ROOT=media_root,
    STATIC_URL="/static/",
    INSTALLED_APPS=installed_apps,
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": "history_db",
            "USER": "history_user2",
            "PASSWORD": "pass",
            "HOST": "db",
            "TEST": {
                "NAME": "test_history_db",
            },
        },
    },
    MIDDLEWARE_CLASSES=[
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "atris.middleware.LoggingRequestMiddleware",
    ],
)


if __name__ == "__main__":
    if not settings.configured:
        settings.configure(**DEFAULT_SETTINGS)
    sys.exit(pytest.main(sys.argv[1:]))
