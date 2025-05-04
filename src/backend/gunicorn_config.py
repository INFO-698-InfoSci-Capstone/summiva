import multiprocessing
import os

# Gunicorn configuration
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Add reload settings if in development mode
if os.environ.get("ENVIRONMENT") == "development":
    reload = True
    # Gunicorn uses different syntax for reload exclusions
    reload_extra_files = []
    # Excluded directories are handled differently in Gunicorn
    # It doesn't support direct exclusions like Uvicorn
