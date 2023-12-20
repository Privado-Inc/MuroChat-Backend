from django.http import JsonResponse

def formatAndReturnResponse(data, status, isUI, pageInfo=None):
    if isUI:
        response = dict()
        response['data'] = data
        if pageInfo:
            response['pageInfo'] = pageInfo
        return JsonResponse(response, safe=False, status=status)
    else:
        return JsonResponse(data, safe=False, status=status)