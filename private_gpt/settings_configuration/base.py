import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

OKTA_INTROSPECT_ENDPOINT = '/oauth2/v1/introspect' #default is required because we are using default endpoint to generate token. idp client it doesn't needed.
SSO_GROUPS_ENDPOINT = '/api/v1/groups' # url='https://trial-9740975.okta.com/api/v1/groups',

OKTA_SUPER_ADMIN_EMAIL = os.getenv('CUSTOMER_OKTA_SUPER_ADMIN_EMAIL')
LOGGING = { 
    'version': 1,
    'crypto_key': b'kspft2Gr2ayWy0mdPAmVwdfmVdFHnvxiXZCU4Ly5Q80=',
}

# REST_FRAMEWORK = {
#     'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.IsAuthenticated',
#     ],
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         'rest_framework.authentication.TokenAuthentication',
    
#     )
# }

# Application definition
INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'rest_framework',
    'rest_framework.authtoken',
    'private_gpt',
    'users.apps.Users',
    'chats',
]

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# 72 hours
TOKEN_EXPIRED_AFTER_SECONDS = 259200

AUTHENTICATION_BACKENDS = [
    'middlewares.PasswordLessLogin.PasswordLessLogin',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_USER_MODEL = 'users.User'

MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_grip.GripMiddleware',
]

ROOT_URLCONF = 'private_gpt.urls'
WSGI_APPLICATION = 'private_gpt.wsgi.application'

ALLOWED_HOSTS=['*']

CORS_ALLOW_HEADERS = ['*']

DATABASES = {
    'default' : {
        'ENGINE': 'djongo',
        'NAME': 'enterprise-users',
        'CLIENT': {
            'name': 'enterprise-users',
            'host': os.getenv('MONGO_HOST'),
            'username': 'enterprise-default-user',
            'password': os.getenv('CONFIG_USERS_PSW'),
            'authSource': '' if os.getenv('MONGO_HOST').endswith(".mongodb.net") else 'privado-users',
        }
    },
    'chat': {
        'HOST': os.getenv('MONGO_HOST'),
        'USERNAME': 'enterprise-default-user',
        'PASSWORD': os.getenv('CONFIG_USERS_PSW'),
        'AUTH_DATABASE': '' if os.getenv('MONGO_HOST').endswith(".mongodb.net") else 'privado-users',
        'DATABASE': 'chat',
    },
    'idp': {
        'HOST': os.getenv('MONGO_HOST'),
        'USERNAME': 'enterprise-default-user',
        'PASSWORD': os.getenv('CONFIG_USERS_PSW'),
        'AUTH_DATABASE': '' if os.getenv('MONGO_HOST').endswith(".mongodb.net") else 'privado-users',
        'DATABASE': 'idp',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [{
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
},]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
PAGE_SIZE = 2
CHAT_GROUPS = ['Today', 'Last 7 Days', 'Last 30 Days', 'Others']

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER') or None
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD') or None
EMAIL_FROM = os.getenv('EMAIL_FROM')
SUPPORT_EMAIL = os.getenv('SUPPORT_EMAIL')
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_KEYFILE = None
CONFIG_UI_HOST = os.getenv('CONFIG_UI_HOST')
