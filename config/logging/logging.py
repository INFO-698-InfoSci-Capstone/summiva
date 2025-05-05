import logging
import logging.config
import yaml
import os
from pathlib import Path

def setup_logging(service_name=None):
    """Configure logging using YAML configuration.
    
    Args:
        service_name: Optional name of the service to use specific logger
    """
    # Get configuration file path
    config_dir = Path(__file__).parent
    log_config_path = config_dir / "logging.yml"
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("/app/logs") if os.getenv("ENVIRONMENT") == "production" else Path("logs")
    logs_dir.mkdir(exist_ok=True, parents=True)
    
    if log_config_path.exists():
        with open(log_config_path, 'r') as f:
            log_config = yaml.safe_load(f)
        
        # Update dynamic paths 
        log_config['handlers']['file']['filename'] = str(logs_dir / "app.log")
        log_config['handlers']['error_file']['filename'] = str(logs_dir / "error.log")
        
        # Add service-specific log files if service name is provided
        if service_name:
            # Add service-specific handler
            log_config['handlers'][f'{service_name}_file'] = {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'json',
                'filename': str(logs_dir / f"{service_name}.log"),
                'maxBytes': 10485760,
                'backupCount': 5,
                'encoding': 'utf8'
            }
            
            # Create or update service logger
            if f'app.{service_name}' not in log_config['loggers']:
                log_config['loggers'][f'app.{service_name}'] = {
                    'handlers': ['console', 'file', f'{service_name}_file'],
                    'level': 'INFO',
                    'propagate': False
                }
        
        # Dynamically set root level based on ENVIRONMENT
        env = os.getenv("ENVIRONMENT", "development")
        if env == "production":
            log_config['root']['level'] = "INFO"
        else:
            log_config['root']['level'] = "DEBUG"
        
        # Apply logging configuration
        logging.config.dictConfig(log_config)
        
        # Get the logger
        logger = logging.getLogger(f"app.{service_name}" if service_name else "app")
        logger.info(f"Logging initialized for {'service: ' + service_name if service_name else 'application'}")
        
        return logger
    else:
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger("app")
        logger.warning(f"⚠️ Warning: {log_config_path} not found, using basic config.")
        return logger