from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utils.TokenExpiryAuthentication import TokenExpiryAuthentication
from django.views.decorators.csrf import csrf_exempt
from utils.Path import verifyPermissions

def view_with_auth_permissions(permission, methods):
    def decorator(view_func):
        @api_view(methods)
        @csrf_exempt
        @authentication_classes([TokenExpiryAuthentication])
        @permission_classes([IsAuthenticated])
        @verifyPermissions(permission)
        def wrapped_view(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)

        return wrapped_view

    return decorator