
from datetime import datetime
from chats.dao.ChatDao import TYPE_OF_AI
from utils.MongoConnection import MongoConnection
from bson.objectid import ObjectId

TYPE_OF_IDP = {
    'OKTA': 'OKTA',
    'GOOGLE': 'GOOGLE',
    'AZURE': 'AZURE',
}

class IDPConfigDao(MongoConnection):

    def __init__(self):
        super(IDPConfigDao, self).__init__('idp')
        self.get_collection("idp_config")

    def createIDPConfig(self, clientId, clientSecret, domain, type, accountId, status):
        return self.collection.update_one(
            {
                'type': TYPE_OF_IDP[type],
            }, {
                "$set": {
                    'type': TYPE_OF_IDP[type],
                    'clientSecret': clientSecret,
                    'clientId': clientId,
                    'domain': domain,
                    'accountId': accountId,
                    'status': status,
                },
                '$currentDate': {
                    'createdAt': { "$type": "date" }
                },
            },
            upsert=True
        )
    
    
    def getIDPConfig(self, type):
        return self.collection.find_one({ "type": type })
