def parseToOpenAIFormat(history):
    openAiFormat = list()
    for message in history:
        openAiFormat.append({
            "role": message["role"],
            "content": message['anonymizedMessage']
        })
    return openAiFormat