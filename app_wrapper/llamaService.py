import logging,requests
import re
from django.http import StreamingHttpResponse
from app_wrapper.commonService import TOKEN_LIMIT, WITH_LAST_N_MESSAGES, numTokenLlama, streamParserHandleInitator

from chats.dao.ChatHistoryDao import TYPE_OF_MESSAGE

log = logging.getLogger(__name__)

def getAI_ResponseFromLlama(modelInfo, message, anonymizedMessage, piiToEntityTypeMap, chatHistory, userId, chatId, isPushedToChatHistory = False):
    
    history = ''
    if chatHistory:
        for messageObj in chatHistory['messages'][WITH_LAST_N_MESSAGES:]:
            if messageObj['type'] == TYPE_OF_MESSAGE['GPT']: # TODO: Change this to system to make it generic
                history += messageObj['anonymizedMessage']
            else:
                history += '[INST] ' + messageObj['anonymizedMessage'] + ' [/INST]'

    if message:
        history += '[INST] ' + anonymizedMessage + ' [/INST]'

    tokens = numTokenLlama(history)
    while tokens >= TOKEN_LIMIT:
        historyArr = history.split('[/INST]')
        historyArr = historyArr[2:]
        history = '[/INST]'.join(historyArr)
        tokens = numTokenLlama(history)

    def event_stream(chatId, isPushedToChatHistory):
        log.info(chatId, history)
        headers = {"Authorization": f"Bearer {modelInfo['secretKey']}"}
        response = requests.post(modelInfo['apiURL'], headers=headers, json={"inputs": history})
        chunk = response.json()
        
        streamParser = streamParserHandleInitator(chatId, isPushedToChatHistory)
        if chunk and len(chunk) > 0:
            chunk = chunk[0].get("generated_text", "").replace("[/INST]", "[INST]")
        else:
            chunk = ""

        newMessages = re.split(r'(\[INST\])', chunk)
        incompleteMessage = ''
        allMessages = []
        for newMsg in newMessages:
            if newMsg.strip() == "[INST]":
                allMessages.append(incompleteMessage.strip())
                incompleteMessage = ''
            elif newMsg.strip() != "[INST]":
                incompleteMessage = incompleteMessage + newMsg

        yield from streamParser(incompleteMessage.lstrip(), userId, message, anonymizedMessage, piiToEntityTypeMap)
        
        # Do Not Delete. This is for streaming
        # aiResponse = ''
        # allMessages = []
        # incompleteMessage = ''
        # isInitialIdentifierRecieved = False
        # streamingStarted = False
        # currenntResponseChunk = ''
        # )
        # lastChunk = ''
        # for chunk in completion:
            # if chunk:
            #     chunk = str(chunk, 'utf-8')
                
            #     if '[{"generated_text":"' in chunk and not isInitialIdentifierRecieved:
            #         isInitialIdentifierRecieved = True
            #         chunk = chunk.replace('[{"generated_text":"', '')
            #     aiResponse = aiResponse + chunk

                #  Another Approach for parser DO NO DELETE
                # currenntResponseChunk = chunk
                # chunk = chunk.replace("[/INST]", "[INST]")

                # newMessages = re.split(r'(\[INST\])', chunk)

                # length = len(newMessages)
                # if (length > 1):
                #     for newMsg in newMessages:
                #         if newMsg.strip() == "[INST]" and incompleteMessage.strip() != "":
                #             allMessages.append(incompleteMessage.strip())
                #             incompleteMessage = ''
                #         elif newMsg.strip() != "[INST]":
                #             incompleteMessage = incompleteMessage + newMsg
                # else:
                #     incompleteMessage = incompleteMessage + chunk

                # newMessages = re.split(r'(\[INST\])', incompleteMessage)
                # length = len(newMessages)
                # if (length > 1):
                #     for newMsg in newMessages:
                #         if newMsg.strip() == "[INST]" and incompleteMessage.strip() != "":
                #             allMessages.append(incompleteMessage.strip())
                #             incompleteMessage = ''
                #         elif newMsg.strip() != "[INST]":
                #             incompleteMessage = incompleteMessage + newMsg
                # else:
                #     incompleteMessage = incompleteMessage + chunk

                # if streamingStarted or aiResponse.startswith(history):
                #     if not streamingStarted:
                #         streamingStarted = True
                #         currenntResponseChunk = incompleteMessage
    
                #     if (currenntResponseChunk.endswith('"}]')):
                #         currenntResponseChunk = currenntResponseChunk.replace('"}]', '')

                # END

                # aiResponsePlain = re.sub(r'[^A-Za-z0-9]+', ' ', aiResponse)
                # if streamingStarted:
                #         completeMessage = lastChunk + chunk
                #         if (completeMessage.endswith('"}]')):
                #             currenntResponseChunk = completeMessage.replace('"}]', '')
                #         else:
                #              currenntResponseChunk = lastChunk
                #              lastChunk = chunk
                # elif len(history) < len(aiResponse) and historyPlain in aiResponsePlain:
                #     streamingStarted = True
                #     lastChunk = aiResponse.replace(history, '').lstrip()
                #     currenntResponseChunk = ''
        
                #     if (currenntResponseChunk.endswith('"}]')):
                #             currenntResponseChunk = currenntResponseChunk.replace('"}]', '')
                    

                # print("Normal Chunks =======>  ", chunk)
                # if streamingStarted and currenntResponseChunk:
                #     print("=======>  ", currenntResponseChunk)
            


    return StreamingHttpResponse(event_stream(chatId, isPushedToChatHistory), content_type='application/json')

