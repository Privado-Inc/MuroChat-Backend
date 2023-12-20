import os
from .base import *

SECRET_KEY = os.getenv('SECRET_KEY')

#TODO: Remove these and replace with specific values as per prod env
ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True
