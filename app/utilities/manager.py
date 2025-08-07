from .lobby import Lobby
from .admin import Admin
import requests
from .log import Logger


class Manager:
    def __init__(self, url, email, password):
        self.url = url
        self.admin = Admin(url, email, password)
        self.lobby = None
        self.logger = Logger.get_logger("Manager")
        self.logger.info(f"Manager initialized with URL: {url}")

    def make_api_request(self, method, endpoint, **kwargs):
        """
        Helper method to make authenticated API requests
        """
        url = self.url + endpoint
        self.logger.debug(f"Making {method.__name__.upper()} request to {url}")
        
        @self.admin.token_required
        def request_with_token(**request_kwargs):
            return method(url, **request_kwargs)
            
        return request_with_token(**kwargs)
            
    def get_lobby_info(self):
        self.logger.warning("get_lobby_info method called but not implemented")
        raise NotImplementedError