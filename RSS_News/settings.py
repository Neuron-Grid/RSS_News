"""
Django settings for RSS_News project.

Generated by 'django-admin startproject' using Django 4.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import os
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-@(84_(j)j5k7oedwb80v(vk+(1m2@nn(sxz9vi+jv!d^#qckf='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 内部アプリ
    'reader',
    # 外部アプリ
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'django.contrib.sites',
    "django_bootstrap5",
    'django_feedparser',
    'django_celery_beat',
    'django_celery_results',
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
            ],
        },
    },
]

WSGI_APPLICATION = 'RSS_News.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
# 授業ノートを参照
# https://scrapbox.io/vantan-prog-xBd7RI6mYx/Django開発3_Dockerとデータベースの設定
# local.env
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mysitedb',
        'USER': 'mysitedbuser',
        'PASSWORD': 'mysitedbpassword',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        # MySQLで日本語が使えるようにする設定
        'OPTIONS': {
            'charset': 'utf8mb4',
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

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 環境変数の設定
env = environ.Env()
env.read_env(os.path.join(BASE_DIR,'local.env'))

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
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"    # メールの送信先をコンソールに出力する
EMAIL_HOST = "smtp.gmail.com"                                       # メールサーバーのホスト名
EMAIL_PORT = "587"                                                  # メールサーバーのポート番号
EMAIL_HOST_USER = "qiye208@gmail.com"                               # メールサーバーのユーザー名
EMAIL_HOST_PASSWORD = "lwvybaboaoimwmvu"                            # メールサーバーのパスワード
EMAIL_USE_TLS = True                                                # TLS暗号化通信を使用する

# CELERY
CELERY_TASK_TRACK_STARTED = True