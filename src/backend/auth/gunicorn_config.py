# Gunicorn configuration file
import multiprocessing

# Binding
bind = "0.0.0.0:8000"

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000

# Timeout
timeout = 30

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "summiva"

# SSL (uncomment if using HTTPS)
# keyfile = "path/to/keyfile"
# certfile = "path/to/certfile"