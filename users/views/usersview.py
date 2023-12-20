import logging
from django.conf import settings

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from users.serializer import serializeUserObject
from users.services.IDPPrivadoRoleMapping import IDPPrivadoRoleMappingService
from utils.PermissionDecorator import view_with_auth_permissions
from utils.Permissions import Permission
from utils.requestValidator import getTheIsUIFlag 
from ..services.userservice import doLoginOrSignup, getIDPData, getSessionUserDetails, getUsersFromOkta, saveIDPData, sendInviteToUsers, \
    showAvailableUsers, getAllUsers, getUserFilters, getOnboardingStatus, handleMetaInformation, resetAPP

log = logging.getLogger(__name__)

idpPrivadoRoleMappingService = IDPPrivadoRoleMappingService()

@api_view(['GET'])
def handleMeta(request):
    isUI = getTheIsUIFlag(request)
    return handleMetaInformation(isUI=isUI)

@api_view(['POST'])
def handleOktaLoginOrSignup(request):
    isUI = getTheIsUIFlag(request)
    userLoginOrSignUpData = JSONParser().parse(request)

    return doLoginOrSignup(userLoginOrSignUpData, isUI=isUI)

@view_with_auth_permissions(
    {
        Permission.ReadIDPConfig: ['GET'],
        Permission.ManageIDPConfig: ['POST', 'GET'],
    },
    ['POST', 'GET']
)
def handleIDP(request):
    isUI = getTheIsUIFlag(request)
    email = request.user.email
    data = request.data
    if request.method == 'GET':
        return getIDPData(isUI)
    if request.method == 'POST':
        user = serializeUserObject(request.user)
        accountId = user["account"]["id"]
        return saveIDPData(email, data, accountId, isUI)

@view_with_auth_permissions(
    {
        Permission.ReadGroups: ['GET'],
        Permission.ManageGroups: ['POST', 'GET'],
    },
    ['POST', 'GET']
)
def handleIDPRoleMapping(request):
    isUI = getTheIsUIFlag(request)

    data = request.data
    if request.method == 'GET':
        return idpPrivadoRoleMappingService.getIdpPrivadoRoleMapping(isUI)
    if request.method in ('POST'):
        user = serializeUserObject(request.user)
        accountId = user["account"]["id"]
        return idpPrivadoRoleMappingService.updateRoleMapping(data, accountId, isUI)

@view_with_auth_permissions(
    {
        Permission.ReadGroups: ['GET'],
    },
    ['GET']
)
def fetchOktaGroups(request):
    isUI = getTheIsUIFlag(request)

    if request.method == 'GET':
        return idpPrivadoRoleMappingService.getOktaRoles(isUI)

@view_with_auth_permissions(
    {
        Permission.ManageOnboarding: ['POST'],
    },
    ['POST']
)
def handleOnboarding(request):
    isUI = getTheIsUIFlag(request)

    if request.method == 'POST':
        return getOnboardingStatus(request.user, isUI)


@api_view(['GET'])
def clearALL(request):
    isUI = getTheIsUIFlag(request)

    return resetAPP(isUI)

@view_with_auth_permissions(
    {
        Permission.ReadUser: '*',
    },
    ['GET']
)
def handleSessionUser(request):
    isUI = getTheIsUIFlag(request)

    user = request.user
    return getSessionUserDetails(user, isUI)


### OLD Views

@view_with_auth_permissions(
    {
        Permission.ManageOkta: '*',
    },
    ['GET']
)
def getUsers(request):
    isUI = getTheIsUIFlag(request)
    userId = request.user.id

    return getUsersFromOkta(userId, isUI)

@view_with_auth_permissions(
    {
        Permission.ManageInviteUsers: ['GET', 'POST'],
        Permission.ReadInviteUsers: ['GET']
    },
    ['GET', 'POST']
)
def inviteUsers(request):
    isUI = getTheIsUIFlag(request)
    userId = request.user.id

    if request.method == 'GET':
        return showAvailableUsers(isUI)
    data = request.data
    if request.method == 'POST':
        return sendInviteToUsers(userId, data, isUI)


@view_with_auth_permissions(
    {
        Permission.WriteShareChat: ['GET']
    },
    ['GET', 'POST']
)
def users(request):
    isUI = getTheIsUIFlag(request)

    if request.method == 'GET':
        return getAllUsers(request, isUI)

@view_with_auth_permissions(
    {
        Permission.ReadUserFilters: ['GET']
    },
    ['GET']
)
def userFilters(request):
    isUI = getTheIsUIFlag(request)
    userId = request.user.id

    return getUserFilters(userId, isUI)
