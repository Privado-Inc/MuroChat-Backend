from django.urls import path

from .views import chatview

urlpatterns = [
    path('chats/<chatId>/message/<messageId>', chatview.handleSingleChatMessage),
    path('chats/<chatId>/message/<messageId>/redacted-meta', chatview.handleRedactedMetadata),
    path('chats/<chatId>/message/<messageId>/bookmark', chatview.handleBookmarks),
    path('chats/bookmark', chatview.getBookmarkedChats),
    path('chats/share', chatview.handleShareChat),
    path('chats/import/<userChatSharingId>/<chatId>', chatview.handleImportChat),
    path('chats/<chatId>/share', chatview.handleShareChat),
    path('chats/<chatId>', chatview.handleSingleChat),
    path('employee-chats', chatview.handleEmployeeChats),
    path('chats', chatview.handleChats),
    path('employee-chats', chatview.handleEmployeeChats),
    path('chat/<chatId>/pin', chatview.handlePinnedChats),
    path('llm_models', chatview.handleLlmModels),
    path('llm_models/<modelId>', chatview.handleLlmModels),
    path('stats', chatview.calculateStats)
]
