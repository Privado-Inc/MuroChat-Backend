from cryptography.fernet import Fernet
from django.conf import settings

crytoClient = None

def getCryptoClient():
    global crytoClient
    if crytoClient is None:
        crytoClient = Fernet(settings.LOGGING['crypto_key'])
    return crytoClient