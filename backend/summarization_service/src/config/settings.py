import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Mongo + Auth
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://mongodb:27017")
    AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000")

    # Celery + RabbitMQ
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672//")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "rpc://")
