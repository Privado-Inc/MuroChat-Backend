from utils.MongoConnection import MongoConnection
from utils.Permissions import Roles


RolePrivilege = {}
RolePrivilege[Roles.USER] = 3
RolePrivilege[Roles.SECURITY_PRIVACY_ADMIN] = 2
RolePrivilege[Roles.IT_ADMIN] = 1

def getHighestPrevilege(roles):
    highestRole = None
    for role in roles:
        if highestRole is None or RolePrivilege[role] > RolePrivilege[highestRole]:
            highestRole = role
    return highestRole

class IDPRoleMappingDao(MongoConnection):

    """
    sample record:
    {
        "_id": Object("somerandomid"),
        "privadoRole": "USER or SECURITY_PRIVACY_ADMIN or IT_ADMIN",
        "idpRoles": [""]
        ""
    }
    """

    def __init__(self):
        super(IDPRoleMappingDao, self).__init__('idp')
        self.get_collection("sso_role_mapping")

    def getPrivadoRole(self, groups):
        matchedRecords = self.collection.find({
            "idpRoles": {"$in": groups}
        })

        matchingRoles = []
        for record in matchedRecords:
            matchingRoles.append(record["privadoRole"])

        highestPrivilegeRole = getHighestPrevilege(matchingRoles)

        return highestPrivilegeRole

    def insertOrUpdate(self, idpPrivadoRoles, accountId):
        result = None
        for idpPrivadoRole in idpPrivadoRoles:
            result = self.collection.update_one({
                'privadoRole': idpPrivadoRole["privadoRole"],
                'accountId': accountId,
            }, {
                '$set': { 'idpRoles': idpPrivadoRole["idpRoles"], **idpPrivadoRole },
            }, upsert=True)
        return result
    
    def getMapping(self):
        return list(self.collection.find({}))
    
