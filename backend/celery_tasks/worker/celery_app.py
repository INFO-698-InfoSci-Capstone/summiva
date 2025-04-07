from celery import Celery
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Celery app
celery_app = Celery(
    'summiva',
    broker=os.getenv('RABBITMQ_URL', 'amqp://guest:guest@rabbitmq:5672//'),
    backend=os.getenv('REDIS_URL', 'redis://redis:6379/0'),
    include=['celery_tasks.worker.tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_queue='default',
    task_queues={
        'default': {
            'exchange': 'default',
            'routing_key': 'default'
        },
        'summarization': {
            'exchange': 'summarization',
            'routing_key': 'summarization'
        },
        'tagging': {
            'exchange': 'tagging',
            'routing_key': 'tagging'
        }
    }
) 