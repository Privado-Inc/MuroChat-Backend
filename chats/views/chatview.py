import logging

from rest_framework.decorators import api_view
from utils.requestValidator import getTheIsUIFlag 
from chats.services.chatService import bookmarkChatMessage, calculateStat, createMessages, deleteChatMessage, deleteChatUserMessage, \
    getBookmarkedChatMessages, getChats, createOrUpdateChatMessage, getChatMessages, getChatsByFilter, \
    selfRemoveFromSharedList, \
    shareChats, getSharedChats, revokeSharedChat, importChat, removeBookmarkChatMessage, \
    updateOrRegenerateChatUserMessage, pinChat, unpinChat, updateChatName, getChatsByPeriod, createLlmModel, \
    getLlmModels, updateLlmModel, deleteModel, getRedactedMetadata
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from utils.TokenExpiryAuthentication import TokenExpiryAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from utils.Permissions import Permission
from utils.PermissionDecorator import view_with_auth_permissions
log = logging.getLogger(__name__)

@view_with_auth_permissions({
    Permission.ManageChat: '*',
    Permission.ReadChat: ['GET'],
    Permission.WriteChat: ['GET',  'POST', 'PUT'],
}, ['POST', 'GET', 'PUT'])
def handleChats(request):
    isUI = getTheIsUIFlag(request)
    userId = request.user.id
    data = request.data
    page = request.GET.get('page', 1)
    pageSize = int(request.GET.get('pageSize', 100))
    searchTerm = request.GET.get('searchTerm')
    groups = request.GET.get('groups')

    if request.method == 'POST':
        return createOrUpdateChatMessage(userId, None, data, isUI)

    if request.method == 'GET':
        if groups == 'True':
            return getChatsByPeriod(userId, isUI)
        return getChats(userId=userId, page=page, pageSize=pageSize, searchTerm=searchTerm, isUI=isUI)

    if request.method == 'PUT':
        chatId = request.data.get('chatId')
        title = request.data.get('name')
        return updateChatName(userId, chatId, title, isUI)
    

@view_with_auth_permissions({
    Permission.ManageChatHistory: '*',
    Permission.ReadChatHistory: ['GET'],
    Permission.WriteChatHistory: ['GET', 'PUT', 'POST', 'DELETE'],
}, ['GET'])
def handleRedactedMetadata(request, chatId):
    isUI = getTheIsUIFlag(request)
    userId = request.user.id
    return getRedactedMetadata(userId, chatId, isUI)


@view_with_auth_permissions({
    Permission.ManageChatHistory: '*',
    Permission.ReadChatHistory: ['GET'],
    Permission.WriteChatHistory: ['GET', 'PUT', 'POST', 'DELETE'],
}, ['PUT', 'GET', 'POST', 'DELETE'])
def handleSingleChat(request, chatId):
    isUI = getTheIsUIFlag(request)
    userId = request.user.id
    page = request.GET.get('page', 1)
    pageSize = int(request.GET.get('pageSize', 100))

    if request.method == 'GET':
        return getChatMessages(userId, chatId, page, pageSize, isUI)

    data = request.data
    if request.method == 'POST':
        return createMessages(userId, chatId, data, isUI)

    if request.method == 'PUT':
        return createOrUpdateChatMessage(userId, chatId, data, isUI)

    if request.method == 'DELETE':
        return deleteChatMessage(userId, chatId, isUI)

@view_with_auth_permissions({
    Permission.ManageChatHistory: '*',
    Permission.WriteChatHistory: ['GET', 'PUT', 'POST'],
}, ['POST', 'PUT', 'DELETE'])
def handleSingleChatMessage(request, chatId, messageId):
    isUI = getTheIsUIFlag(request)
    userId = request.user.id

    if request.method == 'DELETE':
        return deleteChatUserMessage(userId, chatId, messageId, isUI)

    data = request.data
    if request.method == 'PUT':
        return updateOrRegenerateChatUserMessage(userId, chatId, messageId, data, isUI)

    if request.method == 'POST':
        return updateOrRegenerateChatUserMessage(userId, chatId, messageId, data, isUI, isRegenerate = True)

@view_with_auth_permissions(
    {
        Permission.ReadEmployeeChats: ['GET']
    },
    ['GET']
)
def handleEmployeeChats(request):
    isUI = getTheIsUIFlag(request)

    return getChatsByFilter(request, isUI)

@view_with_auth_permissions(
    {
        Permission.ManageBookmarks: ['GET']
    },
    ['GET']
)
def getBookmarkedChats(request):
    isUI = getTheIsUIFlag(request)

    userId = request.user.id
    page = request.GET.get('page', 1)
    pageSize = int(request.GET.get('pageSize', 100))
    bookmarkType = request.GET.get('bookmarkType', None) # ALL, USER_MESSAGE, GPT

    return getBookmarkedChatMessages(userId, page, pageSize, typeFilter=bookmarkType, isUI=isUI)

@view_with_auth_permissions({
    Permission.ManageBookmarks: '*',
}, ['POST', 'DELETE'])
def handleBookmarks(request, chatId, messageId):
    isUI = getTheIsUIFlag(request)
    userId = request.user.id

    if request.method == 'POST':
        return bookmarkChatMessage(userId, chatId, messageId, isUI)

    if request.method == 'DELETE':
        return removeBookmarkChatMessage(userId, chatId, messageId, isUI)

@view_with_auth_permissions(
    {
        Permission.ManagePinnedChats: ['PUT', 'DELETE']
    },
    ['PUT', 'DELETE']
)
def handlePinnedChats(request, chatId):
    isUI = getTheIsUIFlag(request)
    userId = request.user.id

    if request.method == 'PUT':
        return pinChat(userId, chatId, isUI)

    if request.method == 'DELETE':
        return unpinChat(userId, chatId, isUI)
@view_with_auth_permissions(
    {
        Permission.ManageChat: ['POST', 'DELETE', 'GET'],
        Permission.WriteChatHistory: ['POST', 'GET'],
        Permission.ReadChat: ['GET']
    },
    ['POST', 'DELETE', 'GET']
)
def handleShareChat(request, chatId = None):
    isUI = getTheIsUIFlag(request)
    userId = request.user.id
    
    if request.method == 'POST':
        sharedWith = request.data.get("sharedWith", [])
        name = request.data.get('name', None)
        
        return shareChats(userId, chatId, sharedWith, name, isUI)
    
    if request.method == 'GET':
        return getSharedChats(userId, isUI)
    
    if request.method == 'DELETE':
        userIds = request.data.get("userIds", None)
        selfRemove = request.data.get("selfRemove", False)
        if (selfRemove):
            sharedBy = request.data.get("sharedBy", None)
            return selfRemoveFromSharedList(chatId, sharedBy, userId, isUI)
        return revokeSharedChat(chatId, userId, userIds, isUI)

    
@view_with_auth_permissions(
    {
        Permission.WriteChat: ["POST"]
    },
    ["POST"]
)
def handleImportChat(request, userChatSharingId, chatId):
    isUI = getTheIsUIFlag(request)
    userId = request.user.id
    
    if request.method == 'POST':
        return importChat(userChatSharingId, chatId, userId, isUI)

@view_with_auth_permissions(
    {
        Permission.ManageLlmModels: ["POST", "PUT", "GET", "DELETE"]
    },
    ["POST", "PUT", "GET", "DELETE"]
)
def handleLlmModels(request, modelId = None):
    isUI = getTheIsUIFlag(request)
    data = request.data

    if request.method == 'POST':
        return createLlmModel(data, isUI)

    if request.method == 'GET':
        return getLlmModels(isUI)
    
    if request.method == 'DELETE':
        return deleteModel(modelId, isUI)

    if request.method == 'PUT':
        return updateLlmModel(data, modelId, isUI)


@view_with_auth_permissions(
    {
        Permission.ReadEmployeeChats: ['GET']
    },
    ['GET']
)
def calculateStats(request):
    isUI = getTheIsUIFlag(request)

    if request.method == 'GET':
        return calculateStat(isUI)
