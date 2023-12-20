from enum import Enum
from django.conf import settings
from users.dao.idpRoleMappingDao import IDPRoleMappingDao
from users.dao.idpRolesDao import IDPRolesDao
from utils.Permissions import Roles
from utils.responseFormatter import formatAndReturnResponse
from rest_framework import status
import logging, json
from bson.json_util import dumps

log = logging.getLogger(__name__)

class IDPPrivadoRoleMappingService:

    idpRolesDao = IDPRolesDao()
    idpRoleMappingDao = IDPRoleMappingDao()

    @classmethod
    def getOktaRoles(cls, isUI):
        roles = json.loads(dumps(cls.idpRolesDao.getGroups()))
        if len(roles):
            return formatAndReturnResponse(roles, status=status.HTTP_200_OK, isUI=isUI )
        return formatAndReturnResponse([], status=status.HTTP_404_NOT_FOUND, isUI=isUI )

    @classmethod
    def updateSSORoles(cls, data):
        ssoType = 'okta' # TODO - update this once other SSO added or configured
        return cls.idpRolesDao.insert(data, ssoType)

    @classmethod
    def getPrivadoRole(cls, groups):
        return cls.idpRoleMappingDao.getPrivadoRole(groups)
    
    @classmethod
    def getIdpPrivadoRoleMappingData(cls):
       mapping = cls.idpRoleMappingDao.getMapping()
       return mapping

    @classmethod
    def getIdpPrivadoRoleMapping(cls, isUI):
       mapping = json.loads(dumps(cls.idpRoleMappingDao.getMapping()))

       if len(mapping):
           return formatAndReturnResponse(mapping, status=status.HTTP_200_OK, isUI=isUI )
       
       return formatAndReturnResponse([], status=status.HTTP_404_NOT_FOUND, isUI=isUI )

    @classmethod
    def updateRoleMapping(cls, roleMapping, accountId, isUI=False):
        availableRoles = [Roles.IT_ADMIN, Roles.SECURITY_PRIVACY_ADMIN, Roles.USER]
        for role in roleMapping:
            if role["privadoRole"] not in availableRoles:
                return formatAndReturnResponse(
                    {"message": "Invalid Privado Role Passed."}, status=status.HTTP_400_BAD_REQUEST, isUI=isUI
                )
            elif "idpRoles" not in role:
                return formatAndReturnResponse(
                    {"message": "idpRoles key is missing."}, status=status.HTTP_400_BAD_REQUEST, isUI=isUI
                )
    
        result = cls.idpRoleMappingDao.insertOrUpdate(roleMapping, accountId)

        if result:
            return formatAndReturnResponse(
                {"message": "Successfully mapped role"}, status=status.HTTP_200_OK, isUI=isUI
            )
        return formatAndReturnResponse(
                {"message": "Failed to map roles"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR, isUI=isUI
            )
