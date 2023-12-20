import re

def getTheIsUIFlag(request):
    isUI = request.GET.get('isUI')
    if not isUI:
        isUI = False
    return isUI