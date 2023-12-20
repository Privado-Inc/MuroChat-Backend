from pymongo import MongoClient
from django.conf import settings


class RootMongoConnection(object):
    def __init__(self):
        DATABASES = settings.DATABASES
        self.client = MongoClient(host=[DATABASES['chat']['HOST']], username=DATABASES['chat']['USERNAME'], password=DATABASES['chat']['PASSWORD'],
                            authSource=DATABASES['chat']['AUTH_DATABASE'])
        self.client = self.client

    def getDB(self, name):
        self.client[name]