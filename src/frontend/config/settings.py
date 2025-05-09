import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('summiva-frontend')

# --- Backend API Configuration ---
BACKEND_BASE_URL = os.environ.get('BACKEND_BASE_URL', 'http://localhost:8000')
AUTH_SERVICE_URL = f"{BACKEND_BASE_URL}/auth"
SUMMARY_SERVICE_URL = f"{BACKEND_BASE_URL}/summarization"
TAGGING_SERVICE_URL = f"{BACKEND_BASE_URL}/tagging"
GROUPING_SERVICE_URL = f"{BACKEND_BASE_URL}/grouping"
SEARCH_SERVICE_URL = f"{BACKEND_BASE_URL}/search"

# --- Persistent Storage ---
DB_FILE = os.environ.get('DB_FILE', 'summary_db.json')

# --- UI Configuration ---
APP_TITLE = "Summiva - NLP Summarization System"
APP_PORT = int(os.environ.get('PORT', 8080))
APP_DARK_MODE = os.environ.get('DARK_MODE', 'true').lower() == 'true'

# --- App State ---
DEBUG_MODE = os.environ.get('DEBUG', 'false').lower() == 'true'