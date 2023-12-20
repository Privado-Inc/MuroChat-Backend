import base64
import logging
from traceback import format_exception
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

log = logging.getLogger(__name__)


class DjangoEmailClient:

    @classmethod
    def sendEmailWithContent(cls, recipientEmails, subject,  content, fromEmail, reply_to):
        email = EmailMultiAlternatives(subject, strip_tags(content), from_email=fromEmail, to=recipientEmails, reply_to=reply_to)

        email.attach_alternative(content, "text/html")

        return DjangoEmailClient.sendEmailWithReTry(email)

    @classmethod
    def sendEmailWithTemplate(cls, recipientEmails, subject,  templatePath, callbackToUpdateTemplate, fromEmail, reply_to, additionalConf = {}):
        with open(templatePath) as file:
            template = file.read()
            html_content = callbackToUpdateTemplate(template)
            # template = template.replace(
            #     "{{renewUrl}}", renewUrl
            # )

        email = EmailMultiAlternatives(subject, strip_tags(html_content), from_email=fromEmail, to=recipientEmails, reply_to=reply_to)

        email.attach_alternative(html_content, "text/html")

        attachmentConf = additionalConf.get("attachment", None)
        if attachmentConf:
            email.attach(attachmentConf['filename'], base64.b64encode(attachmentConf["fileContent"]).decode(), attachmentConf['fileType'])

        return DjangoEmailClient.sendEmailWithReTry(email)

    @classmethod
    def sendEmailWithReTry(cls, email, trialCount=0):

        try:
            sent_count = email.send()

            if sent_count == 0:
                return DjangoEmailClient.sendEmailWithReTry(email, trialCount + 1)
            elif trialCount == 3:
                raise ChildProcessError('Unable to send Email')
            return True
        except Exception as e:
            log.error(f"Failure while sending your email: {e}")
            return False
