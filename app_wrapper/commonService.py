import json
import logging
import re
from chats.dao.ChatHistoryDao import ChatHistoryDao
from chats.dao.ChatDao import TYPE_OF_AI, ChatDao
import tiktoken
from transformers import LlamaTokenizerFast
from chats.data_firewall.DataFirewall import DataFirewall

TOKEN_LIMIT = 4096
WITH_LAST_N_MESSAGES = -10

log = logging.getLogger(__name__)
chatHistoryDao = ChatHistoryDao()
chatDao = ChatDao()

def update_db(userId, aiResponse, chatId, anonymizedMessage, piiToEntityTypeMap, createdChatHistory): 
    return chatHistoryDao.createOrUpdateChat(userId, chatId, aiResponse, anonymizedMessage, piiToEntityTypeMap, 'GPT', createdChatHistory)

def streamParserHandleInitator(chatId, isPushedToChatHistory):
    aiResponse = ''
    isMetaDataSent = False
    createdChatHistory = False
    chatId = chatId
    isPushedToChatHistory = isPushedToChatHistory

    def streamParser(chunk, userId, message, anonymizedMessage, piiToEntityTypeMap):
        nonlocal aiResponse
        nonlocal isMetaDataSent
        nonlocal createdChatHistory
        nonlocal chatId
        nonlocal isPushedToChatHistory

        if chunk:
            aiResponse = aiResponse + chunk
            if not chatId:
                response = chatDao.createChat(userId, message[:24]) # Here need to get name from the ML which is context of first message
                if response is not None or response.acknowledged:
                    log.info("creating new chat...")
                    chatId = str(response.inserted_id)
            if chatId:
                userMessageId = ''
                if not isPushedToChatHistory:
                    (_, userMessageId) = chatHistoryDao.createOrUpdateChat(userId, chatId, message, anonymizedMessage, piiToEntityTypeMap, 'USER_INPUT', False)
                isPushedToChatHistory = True
                (_, systemMessageId) = update_db(userId, aiResponse, chatId, aiResponse, piiToEntityTypeMap, createdChatHistory)
                createdChatHistory = True
            if not isMetaDataSent:
                yield chatId + "," + userMessageId + "," + systemMessageId + "|-<><>-|" + json.dumps(piiToEntityTypeMap) + "|-<><>-|"
                isMetaDataSent = True
            yield chunk
    return streamParser


def applyDataFirewall(message, exitingPIIMapForChat):
    piiValues = None
    piiToEntityTypeMap = None
    anonymizedMessage = None

    log.info(message)
    for key in exitingPIIMapForChat:
        message = re.sub(re.escape(key), f"<{exitingPIIMapForChat[key]}>", message, flags=re.IGNORECASE)

    log.info(f'parseMessage', message)

    anonymizedMessage, piiValues = DataFirewall.anonymize(message, exitingPIIMapForChat)
    log.info(anonymizedMessage, piiValues)
    piiToEntityTypeMap = DataFirewall.getPiiToEntityMap(piiValues.items, exitingPIIMapForChat)
   
    return anonymizedMessage, piiToEntityTypeMap

def numTokensForGPT(messages, model="gpt-3.5-turbo-0613"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        # print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return numTokensForGPT(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        # print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return numTokensForGPT(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def numTokenLlama(messages):
    tokenizer = LlamaTokenizerFast.from_pretrained("hf-internal-testing/llama-tokenizer")
    tokens = tokenizer.encode(messages)
    return len(tokens)

