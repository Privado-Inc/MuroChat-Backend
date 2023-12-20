from django_slack import slack_message
from django.conf import settings


class Slack:

    def __init__(self):
        pass

    @classmethod
    def sendMessage(cls,message_identifier,message, messageObject):
        slack_message(f'{settings.BASE_DIR}/slack/{message_identifier}.slack', {
            'message': message, 'data': messageObject
        })