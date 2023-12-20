"""
id
user ID 
timestamp
created date 
modified date - last_updated
createdFrom - null / chatId # this is need to know  if the chat is created from shared chat
type (of AI) GPT 
"""
from datetime import datetime
from utils.MongoConnection import MongoConnection
from bson.objectid import ObjectId

TYPE_OF_AI = {
    'GPT': 'GPT',
    'LLAMA': 'LLAMA',
}

class ChatDao(MongoConnection):

    def __init__(self):
        super(ChatDao, self).__init__('chat')
        self.get_collection("chat_meta")

    def getChats(self, userIds=None, searchTerm=None, period=None):
        query = {'isDeleted': False}
        if searchTerm:
            query['name'] = {"$regex": searchTerm, "$options": 'i'}
        if userIds:
            query['userId'] = {'$in': userIds}
        if period:
            query.update(period)

        return self.collection.find(query).sort("modifiedAt", -1)

    def getChat(self, userId, chatId):
        return self.collection.find_one({ 'userId': userId, "_id": ObjectId(chatId) })
    
    def createChat(self, userId, name):
        return self.collection.insert_one({
            'userId': userId,
            'name': name,
            'isDeleted': False,
            'isBookmarked': False,
            'createdAt': datetime.now(),
            'modifiedAt': datetime.now(),
            'type': TYPE_OF_AI['GPT'],
            'createdFrom': None
        })
    
    def importChat(self, chatId, userId, name):
        return self.collection.insert_one({
            'userId': userId,
            'name': name,
            'isDeleted': False,
            'isBookmarked': False,
            'createdFrom': chatId,
            "createdAt": datetime.now(),
            "modifiedAt": datetime.now(),
            'type': TYPE_OF_AI['GPT']
        })

    def getChatsFromIds(self, chatIds):
        return self.collection.find({"_id": {"$in": chatIds}})
    
    def deleteChat(self, userId, chatId):
        return self.collection.update_one({
            'userId': userId,
            '_id': ObjectId(chatId)
        },
        {   "$set": {
                "isDeleted": True,
            }
        })

    def getBookmarkedChats(self, userId):
        return self.collection.find({'userId': userId, "isBookmarked": True, "isDeleted": False })

    def getPinnedChats(self, userId):
        return self.collection.find({'userId': userId, "isPinned": True, "isDeleted": False })

    def bookmarkChat(self, userId, chatId):
        return self.collection.update_one({
            'userId': userId,
            '_id': ObjectId(chatId)
        },
        {   "$set": {
                "isBookmarked": True,
            }
        })

    def removeBookmarkChat(self, userId, chatId):
        return self.collection.update_one({
            'userId': userId,
            '_id': ObjectId(chatId)
        },
        {   "$set": {
                "isBookmarked": False,
            }
        })

    def pinChat(self, userId, chatId):
        return self.collection.update_one({
            'userId': userId,
            '_id': ObjectId(chatId)
        },
        {"$set": {
                "isPinned": True,
            }
        })

    def unpinChat(self, userId, chatId):
        return self.collection.update_one({
            'userId': userId,
            '_id': ObjectId(chatId)
        },
        {"$set": {
                "isPinned": False,
            }
        })

    def updateChatName(self, userId, chatId, name):
        return self.collection.update_one({
            'userId': userId,
            '_id': ObjectId(chatId)
        },
        {"$set": {
                "name": name,
                "modifiedAt": datetime.now(),
            }
        })

    def updateModifiedAt(self, userId, chatId, modifiedAt):
        return self.collection.update_one({
            'userId': userId,
            '_id': ObjectId(chatId)
        },
        {"$set": {
                "modifiedAt": modifiedAt,
            }
        })
