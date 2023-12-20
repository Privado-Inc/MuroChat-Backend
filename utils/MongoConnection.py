from pymongo import MongoClient
from django.conf import settings


class MongoConnection(object):
    def __init__(self, name):
        DATABASES = settings.DATABASES
        self.client = MongoClient(
            host=[DATABASES[name]['HOST']], 
            username=DATABASES[name]['USERNAME'], 
            password=DATABASES[name]['PASSWORD'],
            authSource=DATABASES[name]['AUTH_DATABASE']
        )
        self.db = self.client[DATABASES[name]['DATABASE']]

    def get_collection(self, name):
        self.collection = self.db[name]