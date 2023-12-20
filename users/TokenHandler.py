from rest_framework.authtoken.models import Token

from datetime import timedelta
from django.utils import timezone
from django.conf import settings


def expiresIn(token):
    timeElapsed = timezone.now() - token.created
    leftTime = timedelta(seconds=settings.TOKEN_EXPIRED_AFTER_SECONDS) - timeElapsed
    return leftTime

def isTokenExpired(token):
    return expiresIn(token) < timedelta(seconds=0)

def tokenExpireHandler(token):
    isExpired = isTokenExpired(token)
    if isExpired:
        token.delete()
        token = Token.objects.create(user=token.user)
    return isExpired, token
