from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from users.models import User
from utils.tokenHandler import tokenExpireHandler


class TokenExpiryAuthentication(TokenAuthentication):
    """
    If token is expired then it will be removed
    and new one with different key will be created
    """

    def authenticate_credentials(self, key):

        token = Token.objects.filter(key=key).first()
        if not token:
            return (None, None)

        if not token.user.is_active:
            raise AuthenticationFailed("User is not active")

        is_expired, token = tokenExpireHandler(token)
        if is_expired:
            raise AuthenticationFailed("The Token is expired")

        user = User.objects.get(pk=token.user_id)

        return user, token
