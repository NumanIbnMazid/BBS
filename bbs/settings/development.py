""" # Development Environment Configurations # """
# import common configurations
from bbs.settings.common import *

""" *** Application Allowed Hosts *** """
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

""" *** Database Configuration *** """
# if env.str('DATABASE_URL', default=''):
#     DATABASES = {
#         'default': env.db(),
#     }
# else:
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': BASE_DIR / 'db.sqlite3',
#         }
#     }


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env.str('DB_NAME'),
        'USER': env.str('DB_USER'),
        'PASSWORD': env.str('DB_PASSWORD'),
        'HOST': env.str('DB_HOST'),
        'PORT': env.str('DB_PORT')
    }
}
