from django.urls import path
from utils.Permissions import PermissionList, Permission, RolePermissionsMapping, Roles
from rest_framework.permissions import IsAuthenticated
from utils.TokenExpiryAuthentication import TokenExpiryAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from utils.accessorUtils import getOrNone
from users.models import UserRoleMapping
from utils.responseFormatter import formatAndReturnResponse
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt

def verifyPermission(allowedPermissions, permission):
    return permission in allowedPermissions

def verifyPermissions(permissions):
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if request.user == 'AnonymousUser':
                return formatAndReturnResponse({ 'message': 'Invalid Session'}, status=status.HTTP_403_FORBIDDEN, isUI=True)
            calledMethod = request.method

            print("request.user.id => ", request.user.id)

            roleObj = getOrNone(UserRoleMapping, user_id=request.user.id)
            role = roleObj.role
            if not role:
                raise "No Role found for this user."
            if role == Roles.IT_ADMIN:
                    return view_func(request, *args, **kwargs)
            allowedPermissions = RolePermissionsMapping.getPermissions(role)
            if len(permissions) == 1 and Permission.AllUser in permissions:
                    return view_func(request, *args, **kwargs)

            for permission in permissions:
                if permissions[permission] == '*':
                    if verifyPermission(allowedPermissions, permission):
                        return view_func(request, *args, **kwargs)

                for method in permissions[permission]:
                    if method != calledMethod:
                        continue
                    if verifyPermission(allowedPermissions, permission):
                        return view_func(request, *args, **kwargs)

            return formatAndReturnResponse({ 'message': 'No Authorization found for this method'}, status=status.HTTP_403_FORBIDDEN, isUI=True)

        if len(permissions):
            for permission in permissions:
                if permission not in PermissionList:
                    raise "Invalid Permission > " + permission
            return wrapped_view
        else:
            def wrapped_view(request, *args, **kwargs):
                return view_func(request, *args, **kwargs)
            return wrapped_view

    return decorator