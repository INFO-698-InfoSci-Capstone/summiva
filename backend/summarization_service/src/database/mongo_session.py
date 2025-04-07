from pymongo import MongoClient
from ..config.settings import Settings

settings = Settings()

mongo_client = MongoClient(settings.MONGODB_URI)
mongo_db = mongo_client["summiva_celery_ext_auth"]
