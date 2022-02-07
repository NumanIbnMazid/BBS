""" # Project Common Settings # """
# imports
from bbs.settings.third_party_configs import *
from pathlib import Path
import os
import environ

""" *** Project Directory Configurations *** """
BASE_DIR = Path(__file__).resolve().parent.parent.parent
BASE_APP_DIR = Path(__file__).resolve().parent.parent

""" *** Reading Project Environment *** """
env = environ.Env()
env.read_env(env_file=os.path.join(BASE_DIR, '.env'))

""" *** Application Secret Key *** """
SECRET_KEY = env.str('SECRET_KEY')

""" *** DEBUG Configuration *** """
if env.bool('IS_PRODUCTION', default='') == True:
    DEBUG = False
elif env.bool('IS_PRODUCTION', default='') == False and env.bool('IS_STAGING', default='') == True:
    DEBUG = False
else:
    DEBUG = True

""" *** Application Definations *** """
THIRD_PARTY_APPS = [
    # Django-Allauth Required Apps
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    # Widget Tweaks
    'widget_tweaks',
    # Django Crispy Form
    'crispy_forms',
    'crispy_tailwind',
    # Django Ck Editor
    'ckeditor',
    'ckeditor_uploader',
    # Django Debug Toolbar
    'debug_toolbar',
    # Django Select 2
    'django_select2',
   # 'channels',
]

LOCAL_APPS = [
    'users',
    'posts',
    'plans',
    'utils',
    'faq',
    'chat',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
] + THIRD_PARTY_APPS + LOCAL_APPS + ['django_cleanup.apps.CleanupConfig', ]

""" *** Authentication Definations *** """
AUTH_USER_MODEL = 'users.User'
AUTHENTICATION_BACKENDS = [
    'allauth.account.auth_backends.AuthenticationBackend',
]

""" *** Middlewares Definations *** """
CUSTOM_MIDDLEWARES = [
    # Request Middleware
    'middlewares.middlewares.RequestMiddleware',
    # Django Debug Toolbar Middleware
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
] + CUSTOM_MIDDLEWARES

""" *** Template Definations *** """
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_APP_DIR, 'templates')],
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

""" *** Authentication Password Validators *** """
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

""" *** Localization Configuration *** """
# LANGUAGE_CODE = 'ja'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


""" *** Static & Media Files Configurations *** """
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

from django.utils.translation import gettext_lazy as _

LANGUAGE_CODE = 'en'

LANGUAGES = (
    ('en', _('English')),
    ('ja', _('Japanese')),
)
LOCALE_PATHS =(
    os.path.join(BASE_DIR,'locale/'),
)

STATICFILES_DIRS = [
    os.path.join(BASE_APP_DIR, 'static'),
]
STATIC_ROOT = os.path.join(
    BASE_APP_DIR, os.path.join('static_cdn', 'static_root'))
MEDIA_ROOT = os.path.join(
    BASE_APP_DIR, os.path.join('static_cdn', 'media_root'))

""" *** Other Definations *** """
SITE_ID = 1
ROOT_URLCONF = 'bbs.urls'
WSGI_APPLICATION = 'bbs.wsgi.application'
# For Channel Asgi Application Start
ASGI_APPLICATION = 'bbs.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        }
    }
}
# For Channel Asgi Application End


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
HOME_URL = "/"
INTERNAL_IPS = [
    '127.0.0.1',
]
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        # 'LOCATION': [
        #     '127.0.0.1:11211'
        #     '172.19.26.240:11211',
        #     '172.19.26.242:11211',
        # ]
    },
    "select2": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
             "PASSWORD": env.str('REDIS_PASSWORD', default=''),
             "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Crispy Form Configuraton
CRISPY_FAIL_SILENTLY = not DEBUG

# Tell select2 which cache configuration to use:
SELECT2_CACHE_BACKEND = "select2"

""" *** Third Party Configurations *** """
