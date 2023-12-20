from bson import json_util
from utils.MongoConnection import MongoConnection

class IDPRolesDao(MongoConnection):

    """
    sample record:
    okta
    
    {
        "id": <hashId>,
        "profile": {"name": "", "description": ""},
        "objectClass": [""],
        "type":  "OKTA_GROUP" | "BUILT_IN",
    }

    azure
    {
        "id": "0c1a9d36-d7c8-4608-8b3f-c16cade351df",
        "description": "SecurityGroup1",
        "displayName": "SecurityGroup1",
        "groupTypes": [],
        "mail": null,
        "securityEnabled": true,
        "securityIdentifier": "S-1-12-1-203070774-1174984648-1824604043-3746685869",
        "theme": null,
        "visibility": null,
        "onPremisesProvisioningErrors": [],
        "serviceProvisioningErrors": []
    }
    """

    def __init__(self):
        super(IDPRolesDao, self).__init__('idp')
        self.get_collection("idp_groups")

    def getGroups(self):
        return self.collection.find({})

    def insert(self, data, ssoType):
        for idpGroup in data:
            name = idpGroup.get('profile', { 'name': None }).get("name", None)
            if not name:
                name = idpGroup.get("displayName", None) # Azure key is displayName

            result = self.collection.update_one({
                'id': idpGroup["id"]
            }, {
                '$set': { **idpGroup, "idpName": ssoType, "name": name },
            }, upsert=True)
        return result
    
