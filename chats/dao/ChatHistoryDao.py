from chats.dao.ChatDao import ChatDao
from utils.MongoConnection import MongoConnection
import json, uuid
from datetime import datetime
from bson.json_util import dumps

TYPE_OF_MESSAGE = {
    'GPT': 'GPT',
    'USER_INPUT': 'USER_INPUT'
}

chatDao = ChatDao()
class Messages():
    def __init__(self):
        pass
    
    @staticmethod
    def parseMessage(message, anonymizedMessage, piiToEntityTypeMap, type_of_message):
        messageId = uuid.uuid4().hex
        return {
            'id': messageId,
            'message': message,
            'anonymizedMessage': anonymizedMessage,
            'piiToEntityTypeMap': piiToEntityTypeMap,
            'isDeleted': False,
            'isBookmarked': False,
            'type': TYPE_OF_MESSAGE[type_of_message],
            'createdAt': datetime.now(),
            'modifiedAt': datetime.now()
        }

class ChatHistoryDao(MongoConnection):

    def __init__(self):
        super(ChatHistoryDao, self).__init__('chat')
        self.get_collection("chat_history")

    def createOrUpdateChat(self, userId, chatId, message, anonymizedMessage, piiToEntityTypeMap, type_of_message, updateExistingMessage = False):
        chatHistory = self.collection.find_one({ 'userId': userId, 'chatId': chatId })
        if updateExistingMessage and chatHistory:
            messages = chatHistory['messages']
            messages[-1]['message'] = message
            messages[-1]['anonymizedMessage'] = anonymizedMessage
            chatDao.updateModifiedAt(userId, chatId, datetime.now())

            return (self.collection.update_one({
                    'userId': userId, 'chatId': chatId 
                },
                {
                    "$set": { "messages": messages, "piiToEntityTypeMap": piiToEntityTypeMap }
                }
            ), None)

        message = Messages.parseMessage(message=message, anonymizedMessage=anonymizedMessage, piiToEntityTypeMap=piiToEntityTypeMap, type_of_message=type_of_message)
        messageId = message["id"]

        if chatHistory:
            messages = chatHistory['messages']
            messages.append(message)
            chatDao.updateModifiedAt(userId, chatId, datetime.now())

            return (self.collection.update_one({
                'userId': userId, 'chatId': chatId }, 
                { "$set": { "messages": messages, "piiToEntityTypeMap": piiToEntityTypeMap } }
            ), messageId)
        else:
            return (self.collection.insert_one({
                'userId': userId,
                'chatId': chatId,
                "piiToEntityTypeMap": piiToEntityTypeMap,
                'messages': [message]
            }), messageId)

    def getChatHistory(self, userId, chatId, includeDeleted=False, messageType=None, searchTerm=None):
        type_filter = None
        if messageType == 'system':
            type_filter = 'GPT'
        elif messageType == 'user':
            type_filter = 'USER_INPUT'

        pipeline = [
            {
                "$project": {
                    "userId": 1,
                    "chatId": 1,
                    "piiToEntityTypeMap": 1,
                    "messages": {
                        "$filter": {
                            "input": "$messages",
                            "as": "msg",
                            "cond": {
                                "$and": [
                                    {"$eq": ["$$msg.type", type_filter]} if type_filter else True,
                                    {"$eq": ["$$msg.isDeleted", False]} if not includeDeleted else True,
                                    {"$regexMatch": {"input": "$$msg.message", "regex": searchTerm, "options": "i"}}
                                    if searchTerm else True,
                                ]
                            },
                        }
                    },
                }
            },
            {
                "$match": {
                    "messages": {"$ne": []},
                    "userId": userId,
                    "chatId": chatId,
                }
            },
        ]

        try:
            return self.collection.aggregate(pipeline).next()
        except StopIteration:
            return None

    def deleteMessage(self, userId, chatId, messageId):
        chatHistory = self.collection.find_one({ 'userId': userId, 'chatId': chatId })
        if not chatHistory:
            return None
        isDeleted = False
        for message in chatHistory['messages']:
            if messageId == message['id']:
                isDeleted = True
            if isDeleted:
                message['isDeleted'] = isDeleted

        return self.collection.update_one({
            'userId': userId, 'chatId': chatId }, 
            { "$set": { "messages": chatHistory['messages'] } }
        )

    def getUserChatMessages(self, userId, chatId):
        chat = self.collection.find_one({ 'userId': userId, 'chatId': chatId})
        data = json.loads(dumps(chat))
        messages = data['messages'][::-1]
        user_messages = [item["message"] for item in messages if item["type"] == "USER_INPUT"]
        return user_messages

    def getBookmarkedChatMessages(self, userId, typeFilter, includeDeleted = False):
        elemMatch = {
            "isBookmarked": True,
            "isDeleted": False,
        }
        if typeFilter != "ALL":
            elemMatch["type"] = typeFilter
        
        return self.collection.aggregate([{
            "$match": {
                'userId': userId,
                "messages": {
                    "$elemMatch": elemMatch,
                },
            }
        },{
            "$project": {
                "_id": 0,
                "userId": 1,
                "chatId": 1,
                "name": 1,
                "messages": {
                    "$filter": {
                        "input": "$messages",
                        "as": "message",
                        "cond": { 
                            "$and": [
                                {"$eq": ["$$message.isBookmarked", True ] },
                                {"$eq": ["$$message.isDeleted", False]} if not includeDeleted else True,
                                {"$eq": ["$$message.type", typeFilter ] } if typeFilter != "ALL" else True,
                            ]
                        }
                    }
                }
            }
        }])

    def hasAnyBookmarkMessage(self, userId, chatId):
        return self.collection.count_documents({"userId": userId, "chatId": chatId, "messages.isBookmarked": True})

    def setBookmarkMessage(self, userId, chatId, messageId, isBookmarked):
        return self.collection.update_one(
            {"userId": userId, "chatId": chatId, "messages.id": messageId},
            {"$set": {"messages.$.isBookmarked": isBookmarked}}
        )
    
    def getChatHistoryForShareChat(self, userId, chatId, includeDeleted=False, messageType=None, searchTerm=None):
        type_filter = None
        if messageType == 'system':
            type_filter = 'GPT'
        elif messageType == 'user':
            type_filter = 'USER_INPUT'

        pipeline = [
            {
                "$project": {
                    "piiToEntityTypeMap": 1,
                    "messages": {
                        "$filter": {
                            "input": "$messages",
                            "as": "msg",
                            "cond": {
                                "$and": [
                                    {"$eq": ["$$msg.type", type_filter]} if type_filter else True,
                                    {"$eq": ["$$msg.isDeleted", False]} if not includeDeleted else True,
                                    {"$regexMatch": {"input": "$$msg.message", "regex": searchTerm, "options": "i"}}
                                    if searchTerm else True,
                                ]
                            },
                        }
                    },
                    "chatId": 1,
                    "_id": 0,
                }
            },
            {
                "$match": {
                    "messages": {"$ne": []},
                    "chatId": chatId,
                }
            },
        ]

        try:
            return self.collection.aggregate(pipeline).next()
        except StopIteration:
            return None

    def importChatHistory(self, newChatId, userId, sourceChatHistory):
        if not sourceChatHistory:
            return False

        return self.collection.insert_one({
            'userId': userId,
            'chatId': newChatId,
            'piiToEntityTypeMap': sourceChatHistory['chatMessages'].get("piiToEntityTypeMap", {}),
            'messages': [
                Messages.parseMessage(message["message"], message["anonymizedMessage"], message["piiToEntityTypeMap"], message["type"])
                for message in sourceChatHistory['chatMessages']["messages"]
                if message.get("isDeleted", False) == False
            ]
        })

    def calculateStat(self, period):
        return self.collection.aggregate([
            {
                "$match": {
                    "messages.type": "USER_INPUT",
                    "messages.createdAt": period['createdAt'],
                    # "messages.createdAt": {"$gte": today.replace(hour=0, minute=0, second=0, microsecond=0), "$lt": today.replace(hour=23, minute=59, second=59, microsecond=999)},
                }
            },
            {
                "$addFields": {
                    "piiArray": { "$objectToArray": "$piiToEntityTypeMap" }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "piiArray": 1,
                    "messages": {
                        "$filter": {
                            "input": "$messages",
                            "as": "message",
                            "cond": { 
                                "$and": [
                                    {"$eq": ["$$message.type", "USER_INPUT" ] },
                                ]
                            }
                        }
                    },
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "messageCount": {"$size": "$messages"},
                    "piiCount": { "$sum": { "$size": "$piiArray" } }
                }
            },
            {
                "$group": {
                    "_id": 0, # a group specification must include an _id
                    "totalMessageCount": { "$sum": "$messageCount" },
                    "totalPiiCount": { "$sum": "$piiCount" }
                }
            }
        ])
    
    def calculateTopRedactedSensitiveData(self, period):
        return self.collection.aggregate([
            {
                "$match": {
                    "messages.type": "USER_INPUT",
                    "messages.createdAt": period['createdAt'],
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "piiToEntityTypeMap": 1,
                    "messages": {
                        "$filter": {
                            "input": "$messages",
                            "as": "message",
                            "cond": { 
                                "$and": [
                                    {"$eq": ["$$message.type", "USER_INPUT" ] },
                                ]
                            }
                        }
                    },
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "piiToEntityTypeMap": 1,
                }
            },
        ])

    def calculateUsageAcrossUserGroups(self, period):
        return self.collection.aggregate([
            {
                "$match": {
                    "messages.type": "USER_INPUT",
                    "messages.createdAt": period['createdAt'],
                }
            },
            {
                "$addFields": {
                    "piiArray": { "$objectToArray": "$piiToEntityTypeMap" }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "userId": 1,
                    "piiArray": 1,
                    "messages": {
                        "$filter": {
                            "input": "$messages",
                            "as": "message",
                            "cond": { 
                                "$and": [
                                    {"$eq": ["$$message.type", "USER_INPUT" ] },
                                ]
                            }
                        }
                    },
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "userId": 1,
                    "messageCount": {"$size": "$messages"},
                    "piiCount": { "$sum": { "$size": "$piiArray" } }
                }
            },
            {
                "$group": {
                    "_id": "$userId", # a group specification must include an _id
                    # "userId": 1,
                    "totalMessageCount": { "$sum": "$messageCount" },
                    "totalPiiCount": { "$sum": "$piiCount" }
                }
            }
        ])
    