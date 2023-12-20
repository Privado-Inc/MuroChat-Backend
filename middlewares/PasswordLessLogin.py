from django.contrib.auth.backends import ModelBackend
from users.models import User


class PasswordLessLogin(ModelBackend):
    """Log in to Django after verifying okta token.

    """
    def __init__(self):
        super().__init__()

    def authenticate(self, request, **kwargs):
        username = kwargs.get('username')
        password = kwargs.get('password')
        isIdpUser = kwargs.get('isIdpUser')

        if isIdpUser:
            try:
                return User.objects.filter(email=username).first()
            except User.DoesNotExist:
                return None
        else:
            return super().authenticate(request, username=username, password=password)

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None