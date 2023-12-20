import logging

from rest_framework import status

from utils.responseFormatter import formatAndReturnResponse

log = logging.getLogger(__name__)


def requestHeadersParser(requiredHeaders):
    def decorator(func):
        def _wrapped_view_func(request, *args, **kwargs):
            isUI = request.GET.get('isUI')
            if request.method in ['GET', 'POST', 'PUT', 'DELETE']:
                for requiredHeader in requiredHeaders:
                    valid, message = 1, ""

                    if requiredHeader not in request.headers:
                        log.debug(f"{requiredHeader} header not found")
                        return formatAndReturnResponse(
                            {"message": f"{requiredHeader} was not found"},
                            status.HTTP_400_BAD_REQUEST, isUI)
                    else:
                        if requiredHeader == "idt":
                            jWToken = request.headers.get("idt", None)
                            if not jWToken:
                                return formatAndReturnResponse(
                                       {"message": f"{requiredHeader} was not found"},
                                       status.HTTP_400_BAD_REQUEST, isUI)
                            return func(request, *args, **kwargs, jWToken=jWToken)
                        else:
                            return func(request, *args, **kwargs)
            return func(request, *args, **kwargs)
        return _wrapped_view_func
    return decorator
