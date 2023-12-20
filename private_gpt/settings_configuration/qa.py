import os
from .base import *

SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True
