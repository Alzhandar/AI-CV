import pymongo
from django.conf import settings

def get_mongodb_client():
    client = pymongo.MongoClient(settings.MONGODB_URI)
    return client

def get_mongodb_db():
    client = get_mongodb_client()
    db_name = settings.MONGODB_URI.split('/')[-1]
    return client[db_name]