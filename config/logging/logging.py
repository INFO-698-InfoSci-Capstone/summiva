import logging
import logging.config
import yaml
import os

from utils.paths import path_manager
from core.config.settings import settings

def setup_logging():
    """Configure logging using YAML configuration."""
    log_config_path = path_manager.get_path('config', 'logging.yml')

    if os.path.exists(log_config_path):
        with open(log_config_path, 'r') as f:
            log_config = yaml.safe_load(f)

        # Update dynamic paths from settings
        log_config['handlers']['file']['filename'] = str(settings.LOG_FILE)
        log_config['handlers']['error_file']['filename'] = str(settings.ERROR_LOG_FILE)

        # Ensure the logs directory exists
        path_manager.ensure_dir(settings.LOGS_DIR)

        # Dynamically set root level based on ENVIRONMENT
        env = os.getenv("ENVIRONMENT", "development")
        if env == "production":
            log_config['root']['level'] = "INFO"
        else:
            log_config['root']['level'] = "DEBUG"

        # Apply logging configuration
        logging.config.dictConfig(log_config)
    else:
        logging.basicConfig(level=logging.DEBUG)
        print(f"⚠️ Warning: {log_config_path} not found, using basic config.")