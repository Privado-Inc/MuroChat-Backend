import json
import base64
from rest_framework import status
from urllib.parse import quote, unquote
from users.dao.idpConfig import IDPConfigDao
from users.services.IDPPrivadoRoleMapping import IDPPrivadoRoleMappingService
from users.services.oktaClient import OktaClient
from utils.Permissions import RolePermissionsMapping
from utils.RootMongoConnection import RootMongoConnection
from utils.cryptoClient import getCryptoClient
from utils.dateTimeUtils import convert_bson_datetime_to_string
from utils.responseFormatter import formatAndReturnResponse
from utils.fields import hasMandatoryFieldsProvided
from requests import post, get
from utils.Dictonary import filter as dictFilter
from utils.accessorUtils import getList, getOrNone, getOrCreate
from django.contrib.auth import authenticate
from django.forms.models import model_to_dict
from rest_framework.authtoken.models import Token
from users.models import User, CustomUserManager, UserDetails, UserRoleMapping, Account
from users.TokenHandler import expiresIn, tokenExpireHandler
from users.serializer import serializeUserObject
from django.conf import settings
from django.core.paginator import Paginator
from utils.paginationUtils import paginationMeta
from django.db.models import Q
from utils.Permissions import Roles
import logging
from bson.json_util import dumps

log = logging.getLogger(__name__)

idpConfigDao = IDPConfigDao()
oktaClient = OktaClient()
rootMongo = RootMongoConnection()

def resetAPP(isUI):
    rootMongo.client.drop_database('chat')
    rootMongo.client['idp']['idp_groups'].delete_many({})
    rootMongo.client['idp']['sso_role_mapping'].delete_many({})
    rootMongo.client['enterprise-users']['users_user_accounts'].delete_many({})
    rootMongo.client['enterprise-users']['users_account'].delete_many({})
    rootMongo.client['enterprise-users']['users_user'].delete_many({})
    
    return formatAndReturnResponse(
                {'message': 'Success'}, status=status.HTTP_200_OK, isUI=isUI #Message mapped with UI
            )

def handleMetaInformation(isUI):
    idpConfiguration = idpConfigDao.getIDPConfig("OKTA")
    if not idpConfiguration:
        formatAndReturnResponse(
                {'message': 'NO_IDP_CONFIGURATION: No idp configuration present'}, status=status.HTTP_400_BAD_REQUEST, isUI=isUI #Message mapped with UI
            )
    return formatAndReturnResponse({
        "clientId": idpConfiguration["clientId"],
        "domain": idpConfiguration["domain"],
    }, status=status.HTTP_200_OK, isUI=isUI)
        
def getSessionUserDetails(user, isUI):
    userRole = getOrNone(UserRoleMapping, user_id=user.id)
    user = serializeUserObject(user)
    if not userRole:
        return formatAndReturnResponse(
            {'message': 'NO_ROLE_FOUND: No Role Found for the user'}, status=status.HTTP_400_BAD_REQUEST, isUI=isUI
        )
    return formatAndReturnResponse({
        **user,
        "role": userRole.role,
        "permissions": RolePermissionsMapping.getUIPermissions(userRole.role)
    }, status=status.HTTP_200_OK, isUI=isUI)

def doLoginOrSignup(userLoginOrSignUpData, isUI):
    log.info('doLoginOrSignup')
    mandatoryAttributes = ['token', 'firstName', 'email']

    if not hasMandatoryFieldsProvided(mandatoryAttributes, userLoginOrSignUpData):
        return formatAndReturnResponse(
            {'message': f'INVALID_REQUEST{", ".join(mandatoryAttributes)} are mandatory'}, status=status.HTTP_400_BAD_REQUEST, isUI=isUI
        )
    token = userLoginOrSignUpData["token"]
    email = userLoginOrSignUpData["email"]
    groups = userLoginOrSignUpData.get("groups", [])
    idpConfiguration = idpConfigDao.getIDPConfig("OKTA")

    if not idpConfiguration:
        formatAndReturnResponse(
                {'message': 'NO_IDP_CONFIGURATION: No idp configuration present'}, status=status.HTTP_400_BAD_REQUEST, isUI=isUI #Message mapped with UI
            )

    totalNumberOfUsers = User.objects.count()
    if totalNumberOfUsers == 0:
        if email.lower().strip() != settings.OKTA_SUPER_ADMIN_EMAIL.lower().strip():
            return formatAndReturnResponse(
                {'message': 'Super_Admin_Only_Allowed'}, status=status.HTTP_400_BAD_REQUEST, isUI=isUI #Message mapped with UI
            )
            
    try:
        if oktaClient.verifyToken(token, email, idpConfiguration["clientId"], idpConfiguration["domain"]):
            exitingUser = getOrNone(User, email=email)
            response = oktaClient.fetchOktaGroups(token, idpConfiguration["domain"])
            if (response.status_code == 200):
                IDPPrivadoRoleMappingService.updateSSORoles(json.loads(response.content))

            if exitingUser is None:
                privadoRole = IDPPrivadoRoleMappingService.getPrivadoRole(groups)
                
                if not privadoRole and totalNumberOfUsers != 0:
                    return formatAndReturnResponse(
                        {'message': 'UserNotInvited: Please contact admin for the activation'}, status=status.HTTP_400_BAD_REQUEST, isUI=isUI #Message mapped with UI
                    )

                if privadoRole and totalNumberOfUsers > 0:
                    account = getOrNone(Account)
                    if not account.is_setup_done:
                        return formatAndReturnResponse(
                            {'message': 'Onboarding_Not_Completed: Please contact admin for the activation'}, status=status.HTTP_400_BAD_REQUEST, isUI=isUI #Message mapped with UI
                        )

                password = User.objects.make_random_password() + "1#4@"
                signUpdata ={
                    "firstName": userLoginOrSignUpData["firstName"],
                    "lastName": userLoginOrSignUpData["lastName"],
                    "email": userLoginOrSignUpData["email"],
                    "isOkta": True,
                    "oktaId": userLoginOrSignUpData["id"]
                }
                signUpdata.pop("email")

                user, _ = CustomUserManager().createUser(
                    email=email, password=password, **signUpdata
                )

                user.invitedRole = Roles.IT_ADMIN if totalNumberOfUsers == 0 else privadoRole

                user.is_active = True
                UserRoleMapping.objects.create(user= user, role=user.invitedRole)
                
                if totalNumberOfUsers == 0:
                    account = Account.objects.create(is_setup_done=False, name="")
                else:
                    account = getOrNone(Account)

                user.accounts.add(account.id)

                user.save()
            elif not exitingUser.is_active:
                return formatAndReturnResponse(
                {
                    'message': "UserNotInvited: Please contact admin for the activation",
                }, status=status.HTTP_403_FORBIDDEN, isUI=isUI
            )
            loggedInUser = authenticate(username=email, isIdpUser=True)
            token, _ = getOrCreate(model=Token, user=loggedInUser)
            _, token = tokenExpireHandler(token)
            return formatAndReturnResponse(
                {
                    'user': serializeUserObject(loggedInUser),
                    'expires_in': expiresIn(token),
                    'token': token.key,
                }, status=status.HTTP_200_OK, isUI=isUI
            )
        else:
            return formatAndReturnResponse(
                {'message': 'Token is tampered or expired'}, status=status.HTTP_400_BAD_REQUEST, isUI=isUI
            )
    except Exception as e:
        log.error(e)
        return formatAndReturnResponse(
                    {'message': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR, isUI=isUI
                )

def getUsersFromOkta(userId, isUI):
    url = settings.OKTA_DOMAIN + '/api/v1/users'
    response = get(url, headers={ "Content-type": "application/json", "Accept": "application/json", "Authorization": "SSWS "} )
    response = response.json()
    privadoUsersList = []

    for user in response:
        userObj = getOrNone(model=User, oktaId = user['id'])
        if not userObj:
            privadoUser = User.objects.create(
                oktaId = user['id'],
                email = user['profile']['email'],
                firstName = user['profile']['firstName'],
                lastName = user['profile']['lastName'],
                isOkta = True,
                is_active = False,
                email_verified = False,
                invitor_id = userId
            )

            privadoUserDetails = UserDetails.objects.create(
                user=privadoUser,
                departmentName=user["profile"].get("department", ""),
                organizationName=user["profile"].get("organization", ""),
                isManager=False,
                reportsTo=user["profile"].get("managerId", "")
            )

            privadoUsersList.append(
                {
                    "user": dictFilter(model_to_dict(privadoUser), ("email", "firstName", "lastName")),
                    "details": dictFilter(model_to_dict(privadoUserDetails), ("departmentName", "organizationName", "reportsTo"))
                }
            )
    return formatAndReturnResponse({ "users":  privadoUsersList }, status=status.HTTP_200_OK, isUI=isUI)

def showAvailableUsers(isUI):
    users = list()
    usersQuerySet = getList(model=User, is_active__in = [False], email_verified__in = [False])

    for user in usersQuerySet:
        userDetails = getOrNone(UserDetails, user_id=user.id)
        users.append({
            "user": dictFilter({ **model_to_dict(user), **{ "id": user.id } }, ("email", "firstName", "lastName", "id", "is_active")),
            "details": dictFilter(model_to_dict(userDetails), ("departmentName", "organizationName", "reportsTo")) if userDetails else {}
        })
    return formatAndReturnResponse(users, status=status.HTTP_200_OK, isUI=isUI)

def getUserFilters(userId, isUI):
    details = getList(model=UserDetails).exclude(user_id=userId)
    unique_values = details.values_list('departmentName', 'organizationName', 'reportsTo').distinct()

    filters = []
    filter_info = {
        'departmentName': 'Department',
        'organizationName': 'Organization',
        'reportsTo': 'Manager'
    }

    for index, (field_key, field_label) in enumerate(filter_info.items()):
        field_values = list(set(value[index] for value in unique_values if value[index]))
        if field_values:
            filters.append({'key': field_key, 'label': field_label, 'values': field_values})

    return formatAndReturnResponse(filters, status=status.HTTP_200_OK, isUI=isUI)

def getAllUsers(request, isUI):
    page = request.GET.get('page', 1)
    pageSize = int(request.GET.get('pageSize', 99999))
    department = request.GET.get('departmentName')
    organization = request.GET.get('organizationName')
    manager = request.GET.get('reportsTo')
    searchTerm = request.GET.get('searchTerm')
    userId = request.user.id

    users = list()
    filter_conditions = Q()

    if department:
        filter_conditions &= Q(userdetails__departmentName__in=department.split(','))

    if organization:
        filter_conditions &= Q(userdetails__organizationName__in=organization.split(','))

    if manager:
        filter_conditions &= Q(userdetails__reportsTo__in=manager.split(','))

    if searchTerm:
        filter_conditions &= (Q(firstName__icontains=searchTerm) | Q(lastName__icontains=searchTerm))

    usersQuerySet = getList(model=User).filter(filter_conditions).exclude(id=userId).order_by('id')

    paginator = Paginator(usersQuerySet, pageSize)
    page_obj = paginator.get_page(page)

    for user in page_obj:
        userDetails = getOrNone(UserDetails, user_id=user.id)
        userRole = getOrNone(UserRoleMapping, user_id=user.id)
        users.append({
            "user": dictFilter({ **model_to_dict(user), **{ "id": user.id } }, ("email", "firstName", "lastName", "id", "is_active")),
            "details": dictFilter(model_to_dict(userDetails), ("departmentName", "organizationName", "reportsTo")) if userDetails else {},
            "role": userRole.role if userRole else ''
        })

    meta = paginationMeta(paginator, page_obj, pageSize)
    return formatAndReturnResponse(users, status=status.HTTP_200_OK, isUI=isUI, pageInfo=meta)

def getOnboardingStatus(user, isUI):
    user = serializeUserObject(user)
    
    if user.get("account", None) and user["account"].get("is_setup_done", False):
        return formatAndReturnResponse({ "ok": True }, status=status.HTTP_200_OK, isUI=isUI)
    
    if not user.get("account", None):
        return formatAndReturnResponse({ "message": "Not authorized for onboarding." }, status=status.HTTP_400_BAD_REQUEST, isUI=isUI)

    idpMappingData = IDPPrivadoRoleMappingService.getIdpPrivadoRoleMappingData()
    idpConfig = json.loads(dumps(idpConfigDao.getIDPConfig("OKTA")))
    ## Add Models checking as well.

    if len(idpMappingData) == 0 or not idpConfig:
        return formatAndReturnResponse({ "ok": False }, status=status.HTTP_200_OK, isUI=isUI)
    
    account = Account.objects.get(id = user["account"]["id"])
    account.is_setup_done = True
    account.save()

    return formatAndReturnResponse({ "ok": True }, status=status.HTTP_200_OK, isUI=isUI)

def getInviteLink(email, verificationKey, firstName, lastName):

    url: str = getattr(settings, 'BACKEND_HOST', 'http://localhost:8000/') + \
                getattr(settings, 'BACKEND_VERIFY_EMAIL_PATH', 'http://localhost:4001/login')
    secret = json.dumps(
        dict(
            email=email,
            evKey=verificationKey,
            firstName=firstName,
            lastName=lastName
        )
    )
    secret_bytes = secret.encode('ascii')
    base64_bytes = base64.b64encode(secret_bytes)
    base64_secret = base64_bytes.decode('ascii')
    base64_secret = quote(base64_secret.encode('utf8'))
    return url + "?secretCode=" + base64_secret

def sendInviteToUsers(userId, data, isUI):
    updatedUsers = list()

    if len(data['users']) == 0:
        return formatAndReturnResponse({ 'message': 'At least one user required.' }, status=status.HTTP_400_BAD_REQUEST, isUI=isUI)

    for user in data['users']:
        userObj = getOrNone(model=User, id = user['userId'])

        if userObj:
            userObj.evKey = User.objects.make_random_password() + "tmp"
            userObj.is_active = user['enable']
            userObj.save()
            updatedUsers.append(user)

            if (user['enable']):
                userRole = getOrNone(UserRoleMapping, user_id=user['userId'])
                if userRole:
                    userRole.role = user["role"]
                else:
                    UserRoleMapping.objects.create(user= userObj, role=user["role"])

                url = getInviteLink(
                    email=userObj.email,
                    verificationKey=userObj.evKey,
                    firstName=userObj.firstName,
                    lastName=userObj.lastName
                )

                # _ = EmailService.sendVerifyEmailMessage(
                #         userObj.email, url
                # )

    return formatAndReturnResponse({ 'message': 'Sent invite to following users', 'users': updatedUsers}, status=status.HTTP_200_OK, isUI=isUI)

def getIDPData(isUI):
    log.info('getIDPData')
    idpConfig = json.loads(dumps(idpConfigDao.getIDPConfig("OKTA")))
    if idpConfig:
        crypto = getCryptoClient()
        idpConfig["clientSecret"] = crypto.decrypt(idpConfig["clientSecret"].encode('utf-8')).decode('utf-8') if idpConfig["clientSecret"] else ""
        idpConfig["createdAt"] = convert_bson_datetime_to_string(idpConfig["createdAt"])

        return formatAndReturnResponse(idpConfig, status=status.HTTP_200_OK, isUI=isUI)
    return formatAndReturnResponse({'message': 'No configuration present'}, status=status.HTTP_404_NOT_FOUND, isUI=isUI)


def saveIDPData(email, data, accountId, isUI):
    log.info('saveIDPData')
    mandatoryAttributes = ['clientId', 'domain', 'type']

    if not hasMandatoryFieldsProvided(mandatoryAttributes, data):
        return formatAndReturnResponse(
            {'message': f'{", ".join(mandatoryAttributes)} are mandatory'}, status=status.HTTP_400_BAD_REQUEST, isUI=isUI
        )
    
    verificationStatus = 0
    isOktaGroupFetched = False
    if oktaClient.verifyToken(data['token'], email, data['clientId'], data["domain"]):
        verificationStatus = 1
        response = oktaClient.fetchOktaGroups(data['token'], data["domain"])
        if (response.status_code == 200):
            IDPPrivadoRoleMappingService.updateSSORoles(json.loads(response.content))
            isOktaGroupFetched = True
        crypto = getCryptoClient()
        clientSecret = crypto.encrypt(data.get("clientSecret", "").encode('utf-8')).decode('utf-8')
        
        idpConfig = idpConfigDao.createIDPConfig(data['clientId'], clientSecret, data["domain"], data["type"], accountId, verificationStatus)
        if verificationStatus and idpConfig:
            return formatAndReturnResponse({ 'message': 'Successfully Saved IDP Config data', 'isOktaGroupFetched': isOktaGroupFetched}, status=status.HTTP_200_OK, isUI=isUI)
    return formatAndReturnResponse({'message': 'Error when saving or verifying IDP Config data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR, isUI=isUI)
