"""
id
modelVersion
secretKey
createdAt
modifiedAt
"""
from bson import ObjectId

from utils.MongoConnection import MongoConnection
from datetime import datetime
import json
from bson.json_util import dumps

class LlmModelDao(MongoConnection):

    def __init__(self):
        super(LlmModelDao, self).__init__('chat')
        self.get_collection("llm_models")

    def createLlmModel(self, modelType, modelVersion, secretKey, apiURL):
        isDefault = False
        if not len(json.loads(dumps(self.getLlmModels()))): # if first and only model - make it default by default
            isDefault = True
        return self.collection.insert_one({
            'modelVersion': modelVersion,
            'secretKey': secretKey,
            "apiURL": apiURL,
            'type': modelType,
            "isDefault": isDefault,
            'createdAt': datetime.now(),
            'modifiedAt': datetime.now(),
        })

    def getLlmModels(self):
        return self.collection.find()

    def updateLlmModel(self, id, modelType, modelVersion, secretKey, apiURL, isDefault):
        result = self.collection.update_one({
            '_id': ObjectId(id)
        },
        {   "$set": {
                "modelVersion": modelVersion,
                "secretKey": secretKey,
                "apiURL": apiURL,
                'type': modelType,
                "isDefault": isDefault,
                "modifiedAt": datetime.now(),
            }
        })
        if isDefault:
            return self.collection.update_many({'_id': {'$ne': ObjectId(id)}},
                        {'$set': {'isDefault': False}})
        return result

    def updateLlmModelIsDefault(self, id):
        self.collection.update_many({}, { "$set": { "isDefault": False } })

        return self.collection.update_one({
            '_id': ObjectId(id)
        },
        {   "$set": {
                "isDefault": True,
                "modifiedAt": datetime.now(),
            }
        })

    def getLlmModel(self, id):
        return self.collection.find_one({ "_id": ObjectId(id) })


    def getDefaultLlmModel(self):
        return self.collection.find_one({ "isDefault": True })
    
    def deleteModel(self, id):
        models = self.getLlmModel(id)
        if (models["isDefault"]):
            return None
        return self.collection.delete_one({ "_id": ObjectId(id) })