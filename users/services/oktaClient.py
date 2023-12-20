import logging
import traceback
import requests

from django.conf import settings
log = logging.getLogger(__name__)


class OktaClient:

    @classmethod
    def fetchOktaGroups(cls, token, domain):
        try:
            response = requests.get(
                url= domain + settings.SSO_GROUPS_ENDPOINT,
                headers={
                    "Authorization": "Bearer " + token,
                    "Accept": "application/json" ,
                    "Content-Type": "application/json" ,
                }
            )
            return response
        except Exception as e:
            exceptionTrace = traceback.format_exc()
            message = f"Failure while getting account info " \
                      f" exceptionTrace: {exceptionTrace}" \
                      f" Exception: {str(e)}"
            log.error(message)
        return None

    @classmethod
    def verifyToken(cls, token, email, clientId, domain):
        try:
            response = requests.post(
                url= domain + settings.OKTA_INTROSPECT_ENDPOINT,
                data={
                    "client_id": clientId,
                    "token_type_hint": "access_token",
                    "token": token
                },
                headers={
                    "Content-type": "application/x-www-form-urlencoded"
                }
            )
            if response.status_code == 200:
                data = response.json()

                client_id = clientId
                if data.get("client_id") == client_id and data.get("active") == True and data.get("username") == email:
                    return True

        except Exception as e:
            exceptionTrace = traceback.format_exc()
            message = f"Failure while getting account info " \
                      f" exceptionTrace: {exceptionTrace}" \
                      f" Exception: {str(e)}"
            log.error(message)

        return False