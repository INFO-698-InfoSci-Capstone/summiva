# src/backend/auth/utils/logging.py

from config.logs.logging import setup_logging

# Re-export the central logging setup
def get_logger(module_name=None):
    """
    Get a logger for the auth service
    
    Args:
        module_name (str, optional): Sub-module name within the auth service
        
    Returns:
        logging.Logger: Configured logger
    """
    service_name = "auth"
    if module_name:
        logger_name = f"{service_name}.{module_name}"
    else:
        logger_name = service_name
        
    return setup_logging(logger_name)