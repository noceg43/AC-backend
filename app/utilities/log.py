import logging
import inspect
import os
from flask import current_app, has_app_context

class Logger:
    @staticmethod
    def get_logger(name=None):
        if name is None:
            # Automatically get the name of the calling class or module
            frame = inspect.currentframe().f_back
            name = frame.f_globals["__name__"]
            if "self" in frame.f_locals:
                name = frame.f_locals["self"].__class__.__name__

        logger = logging.getLogger(name)
        if not logger.hasHandlers():
            # Determine environment (production or development)
            is_production = Logger._is_production_environment()
            
            # Set the logging level based on environment
            if is_production:
                logger.setLevel(logging.WARNING)  # Less verbose in production
            else:
                logger.setLevel(logging.DEBUG)    # More verbose in development

            # Create a console handler
            console_handler = logging.StreamHandler()
            if is_production:
                console_handler.setLevel(logging.WARNING)
            else:
                console_handler.setLevel(logging.DEBUG)

            # Create a formatter and set it for the handler
            if is_production:
                # Simpler format in production without potentially sensitive details
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            else:
                # More detailed format in development
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            
            console_handler.setFormatter(formatter)

            # Add the handler to the logger
            logger.addHandler(console_handler)

        return logger
    
    @staticmethod
    def _is_production_environment():
        """Check if the current environment is production."""
        flask_env = os.environ.get('FLASK_ENV', '').lower()
        debug = os.environ.get('FLASK_DEBUG', '').lower()
        
        if flask_env == 'production':
            return True
        if flask_env == 'development':
            return False
        if debug in ('0', 'false'):
            return True
        if debug in ('1', 'true'):
            return False
            
        # Default to development for safety
        return False
        
    @staticmethod
    def format_error_for_response(exception, include_details=None):
        """Format exception information for API responses.
        In production, detailed error messages are hidden unless explicitly requested.
        """
        if include_details is None:
            # If not specified, include details only in development
            include_details = not Logger._is_production_environment()
            
        if include_details:
            return f"Error: {str(exception)}"
        else:
            return "An error occurred. Please contact the administrator."