import multiprocessing
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = int(os.getenv('MAX_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
timeout = int(os.getenv('TIMEOUT', 120))
keepalive = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = os.getenv('LOG_LEVEL', 'info')

# Process naming
proc_name = 'durga_karma'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None 