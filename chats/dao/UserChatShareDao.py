"""
id
chatId
sharedWith
sharedBy
createdAt
name
"""

from datetime import datetime
from chats.dao.ChatHistoryDao import ChatHistoryDao
from utils.MongoConnection import MongoConnection
from bson.objectid import ObjectId

chatHistoryDao = ChatHistoryDao()

class UserChatShareDao(MongoConnection):

    def __init__(self):
        super(UserChatShareDao, self).__init__('chat')
        self.get_collection("user_chat_sharing")

    def shareChat(self, sharedBy, chatId, sharedWith = [], name = None):
        chatMessages = chatHistoryDao.getChatHistoryForShareChat(sharedBy, chatId)

        # Can create initial sharing and also support more users to add later to the same chat
        return self.collection.update_one(
            {'sharedBy': sharedBy, "chatId": chatId },
            {
                "$set": {'sharedBy': sharedBy, "chatId": chatId, "name": name,  "chatMessages": chatMessages},
                "$addToSet": {"sharedWith": { "$each": sharedWith }},
                '$currentDate': {
                    'createdAt': { "$type": "date" }
                },
            },
            upsert=True
        )

    def getChatIdsSharedByUser(self, sharedBy):
        pipeline = [
            {"$match": { 'sharedBy': sharedBy }},  # Match shared chat documents
            {
                "$project": {
                    "id": {"$toString": "$_id"},  # Convert ObjectId to string
                    "sharedBy": 1,  # Include other properties you want
                    "chatId": 1,
                    "name": 1,
                    "sharedWith": 1,
                    "chatMessages": 1,
                    "_id": 0  # Exclude "_id" from the result
                }
            }
        ]
        return list(self.collection.aggregate(pipeline))

    def getChatIdsSharedWithUser(self, userId):
        pipeline = [
            {"$match": {"sharedWith": {"$in": [userId]}}},  # Match shared chat documents
            {
                "$project": {
                    "id": {"$toString": "$_id"},  # Convert ObjectId to string
                    "sharedBy": 1,  # Include other properties you want
                    "chatId": 1,
                    "name": 1,
                    "sharedWith": 1,
                    "chatMessages": 1,
                    "_id": 0  # Exclude "_id" from the result
                }
            }
        ]
        sharedChats = list(self.collection.aggregate(pipeline))
        return sharedChats
    
    def revokeSharedChatAccess(self, chatId, sharedBy, userIds = None):
        if userIds == None:
            return self.collection.delete_one({"chatId": chatId, 'sharedBy': sharedBy })

        return self.collection.update_one(
            {"chatId": chatId, 'sharedBy': sharedBy },
            {"$pullAll": {"sharedWith": userIds}}
        )
    
    def excludeFromSharing(self, chatId, sharedBy, userId):
        return self.collection.update_one(
            {"chatId": chatId, 'sharedBy': sharedBy },
            {"$pullAll": {"sharedWith": [userId]}}
        )
    
    def isChatIdSharedWithTheUser(self, chatId, userId):
        return self.collection.find_one({"chatId": chatId, "sharedWith": { "$in": [userId] } })

    def getSharedChatHistory(self, id, chatId):
        return self.collection.find_one({"_id": ObjectId(id), "chatId": chatId })
