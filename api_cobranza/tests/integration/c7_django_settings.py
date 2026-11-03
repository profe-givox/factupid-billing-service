import os
import time

from factupid.settings import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["C7_DJANGO_DB_NAME"],
        "USER": os.environ.get("C7_DJANGO_DB_USER", "postgres"),
        "PASSWORD": os.environ.get("C7_DJANGO_DB_PASSWORD", "postgres"),
        "HOST": os.environ.get("C7_DJANGO_DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("C7_DJANGO_DB_PORT", "5433"),
        "OPTIONS": {"sslmode": "disable"},
    }
}

COBRANZA_WEBHOOK_SECRET = os.environ["C7_WEBHOOK_SECRET"]
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
DEBUG = False

C7_DELAY_FILE = os.environ.get("C7_DELAY_FILE", "/tmp/opencode/c7/delay_seconds")
C7_REQUEST_LOG = os.environ.get("C7_REQUEST_LOG", "/tmp/opencode/c7/requests.log")


class C7DelayMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/checkout/complete/" and request.method == "POST":
            try:
                with open(C7_REQUEST_LOG, "a", encoding="utf-8") as log:
                    log.write(f"{time.time()}\n")
            except OSError:
                pass
            try:
                with open(C7_DELAY_FILE, encoding="utf-8") as handle:
                    delay = float(handle.read().strip() or "0")
            except (OSError, ValueError):
                delay = 0
            if delay > 0:
                time.sleep(delay)
        return self.get_response(request)


MIDDLEWARE = list(MIDDLEWARE) + ["c7_django_settings.C7DelayMiddleware"]
