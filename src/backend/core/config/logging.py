import logging
import logging.config
import yaml
from utils.paths import path_manager
from core.config.settings import settings

def setup_logging():
    """Configure logging using YAML configuration."""
    log_config_path = path_manager.get_path('config', 'logging.yml')
    
    with open(log_config_path, 'r') as f:
        log_config = yaml.safe_load(f)
    
    # Update log file paths in configuration
    log_config['handlers']['file']['filename'] = str(settings.LOG_FILE)
    log_config['handlers']['error_file']['filename'] = str(settings.ERROR_LOG_FILE)
    
    # Ensure log directory exists
    path_manager.ensure_dir(settings.LOGS_DIR)
    
    # Apply logging configuration
    logging.config.dictConfig(log_config)

# Initialize logging when module is imported
setup_logging() 