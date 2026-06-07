"""
VOPT Business — Django Settings
"""
import os
from pathlib import Path
from datetime import timedelta
import secrets

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = lambda *args, **kwargs: None

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ─── Segurança ───────────────────────────────────────────────────────────────
DEBUG = os.getenv("APP_ENV", "development") == "development"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = secrets.token_urlsafe(64)
    else:
        raise RuntimeError(
            "DJANGO_SECRET_KEY não encontrado. Crie um arquivo .env ou defina a variável de ambiente."
        )

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# ─── Apps ────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    # Django core — admin removido pois usamos API pura
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Terceiros
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    # VOPT
    "usuarios",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",          # deve ser o primeiro
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "vopt.urls"
WSGI_APPLICATION = "vopt.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres.jdpcyipujxfgazfbywml",
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": "aws-1-us-east-2.pooler.supabase.com",
        "PORT": "6543",
    }
}

# ─── Auth customizado ─────────────────────────────────────────────────────────
AUTH_USER_MODEL = "usuarios.Usuario"

# Validadores de senha do Django (já embutidos)
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ─── Templates ───────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ─── DRF ─────────────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
    # Erros 404/405 em JSON, não HTML
    "EXCEPTION_HANDLER": "usuarios.utils.vopt_exception_handler",
}

# ─── JWT ─────────────────────────────────────────────────────────────────────
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":  timedelta(minutes=int(os.getenv("JWT_EXPIRE_MINUTES", "60"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS":  True,
    "BLACKLIST_AFTER_ROTATION": False,   # ative se adicionar blacklist app
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ─── CORS ────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000"
).split(",")
CORS_ALLOW_CREDENTIALS = True

# ─── Rate limiting (django-ratelimit) ────────────────────────────────────────
RATELIMIT_USE_CACHE = "default"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# ─── Misc ────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = "pt-br"
TIME_ZONE     = "America/Sao_Paulo"
USE_I18N      = True
USE_TZ        = True
STATIC_URL    = "/static/"

# ─── E-mail Services & URLs ───────────────────────────────────────────────────
SENDGRID_API_KEY    = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "noreply@vopt-mail.com")

RESEND_API_KEY      = os.getenv("RESEND_API_KEY")
RESEND_FROM_EMAIL   = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")

SITE_URL            = os.getenv("SITE_URL", "http://127.0.0.1:8000")

# Em produção — reforça HTTPS
if not DEBUG:
    SECURE_SSL_REDIRECT            = True
    SESSION_COOKIE_SECURE          = True
    CSRF_COOKIE_SECURE             = True
    SECURE_BROWSER_XSS_FILTER      = True
    SECURE_CONTENT_TYPE_NOSNIFF    = True
    SECURE_HSTS_SECONDS            = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
