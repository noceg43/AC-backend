import os

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a_default_secret_key')
    DEBUG = False
    TESTING = False

    def __init__(self):
        self.URL = os.environ.get("URL")
        self.EMAIL = os.environ.get("EMAIL")
        self.PASSWORD = os.environ.get("PASSWORD")

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    pass

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
