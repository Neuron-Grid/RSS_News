"""
Django settings for RSS_News project.

Generated by 'django-admin startproject' using Django 4.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

from pathlib import Path
import environ
import os

# 環境変数の設定
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
env.read_env(os.path.join(BASE_DIR, 'service.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env('HOSTS').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.auth',
    # 内部アプリ
    'reader',
    # 外部アプリ
    'allauth.socialaccount',
    'django.contrib.sites',
    'django_feedparser',
    "django_bootstrap5",
    'allauth.account',
    'allauth',
    # フィードの自動更新
    'django_celery_results',
    'django_celery_beat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'RSS_News.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'RSS_News.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.mysql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST':'127.0.0.1',
        'PORT':'3306',
        'OPTIONS': {
            'charset':'utf8mb4',
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'ja'
TIME_ZONE = 'Asia/Tokyo'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redis settings
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"

# Celery settings
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/2'
CELERY_RESULT_BACKEND = f"db+mysql://{env('DB_USER')}:{env('DB_PASSWORD')}@127.0.0.1/{env('DB_NAME')}"
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_TASK_TRACK_STARTED = True
CELERY_TIMEZONE = 'Asia/Tokyo'

# Allauthの設定
SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',            #デフォルトの認証基盤 
    'allauth.account.auth_backends.AuthenticationBackend',  # メールアドレスとパスワードの両方を用いて認証するために必要
)

ACCOUNT_AUTHENTICATION_METHOD = 'email'                 # メールアドレス（とパスワードで）認証する
ACCOUNT_USERNAME_REQUIRED = True                        # 新規登録の時にユーザーネームを尋ねる
ACCOUNT_EMAIL_REQUIRED = True                           # 新規登録の時にメールアドレスを尋ねる
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'                # メール検証を必須とする

LOGIN_URL = '/accounts/login/'                          # ログインURLの設定
LOGIN_REDIRECT_URL = '/feed_list'                       # ログイン後のリダイレクト先
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login/'        # ログアウト後のリダイレクト先

# メールの設定
EMAIL_HOST = env('EMAIL_HOST')                          # メールサーバーのホスト名
EMAIL_PORT = env('EMAIL_PORT')                          # メールサーバーのポート番号
EMAIL_HOST_USER = env('EMAIL_HOST_USER')                # メールサーバーのユーザー名
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')        # メールサーバーのパスワード
EMAIL_USE_TLS = True                                    # TLS暗号化通信を使用する