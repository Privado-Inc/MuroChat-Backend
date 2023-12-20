import logging
from .djangoEmailClient import DjangoEmailClient
from django.conf import settings

log = logging.getLogger(__name__)

class EmailClient:

    @classmethod
    def sendEmailWithContent(cls, recipientEmails, subject,  content, fromEmail=settings.EMAIL_FROM, reply_to=[settings.SUPPORT_EMAIL]):
        return DjangoEmailClient.sendEmailWithContent(recipientEmails, subject,  content, fromEmail, reply_to)

    @classmethod
    def sendEmailWithTemplate(cls, recipientEmails, subject,  templatePath, callbackToUpdateTemplate, fromEmail=settings.EMAIL_FROM, reply_to=[settings.SUPPORT_EMAIL], additionalConf = {}):
        return DjangoEmailClient.sendEmailWithTemplate(recipientEmails, subject,  templatePath, callbackToUpdateTemplate, fromEmail, reply_to, additionalConf)
