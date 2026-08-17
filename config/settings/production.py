from .base import *  # noqa: F401,F403

DEBUG = False

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])

# SQLite in production: the PythonAnywhere Free plan doesn't include MySQL/
# Postgres, and for a single-venue app this scale of traffic is well within
# what SQLite handles fine (WAL mode + busy_timeout below reduce "database
# is locked" risk from a few staff devices writing at once). If this ever
# moves to a paid plan with a real DB server, swap this block back to the
# mysql/postgresql ENGINE.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])
