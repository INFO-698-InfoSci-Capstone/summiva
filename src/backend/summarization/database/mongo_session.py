from config.settings.settings import Settings
from pymongo import MongoClient

settings = Settings()

mongo_client = MongoClient(settings.MONGODB_URI)
mongo_db = mongo_client["summiva_celery_ext_auth"]
