# src/backend/grouping/utils/logging.py

from config.logs.logging import setup_logging

# Re-export the central logging setup
def get_logger(module_name=None):
    """
    Get a logger for the grouping service
    
    Args:
        module_name (str, optional): Sub-module name within the grouping service
        
    Returns:
        logging.Logger: Configured logger
    """
    service_name = "grouping"
    if module_name:
        logger_name = f"{service_name}.{module_name}"
    else:
        logger_name = service_name
        
    return setup_logging(logger_name)
