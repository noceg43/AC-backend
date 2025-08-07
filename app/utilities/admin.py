from .log import Logger
import requests
from functools import wraps


class Admin:
    def __init__(self, url, email, password):
        self.logger = Logger.get_logger() 
        self.logger.debug("Initializing Admin object with URL: %s, Email: %s", url, email)
        self.email = email
        self.password = password
        self.url = url
        self.token = None
        self.header = None
        if not self.authenticate():
            self.logger.error("Authentication failed for Admin with email: %s", email)
            raise Exception("CANNOT LOGIN")
        self.update_header()

    def update_header(self):
        if self.token:
            self.header = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.token
            }
            self.logger.debug("Header updated with token.")
        else:
            self.logger.warning("Token is not available. Header not updated.")

    def authenticate(self):
        auth_url = self.url + "api/auth/admins/login"
        payload = {
            "email": self.email,
            "password": self.password
        }
        self.logger.info("Attempting to authenticate Admin with email: %s", self.email)
        response = requests.post(auth_url, data=payload)
        if response.status_code == 201:
            self.token = response.json()["token"]
            self.update_header()
            self.logger.info("Authentication successful. Token received.")
            return True
        else:
            self.logger.error("Authentication failed. Status code: %d, Message: %s",
                              response.status_code, response.json().get("message", "No message"))
            return False

    def refresh_token(self):
        self.logger.info("Attempting to refresh token for Admin with email: %s", self.email)
        return self.authenticate()
        
    def token_required(self, func):
        """
        A decorator that adds authorization header to requests and refreshes the token on 403 errors.
        
        Usage:
        @admin.token_required
        def my_api_request(url, **kwargs):
            return requests.get(url, **kwargs)
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'headers' not in kwargs:
                kwargs['headers'] = {}
            
            # Update headers with token if available
            if self.header:
                kwargs['headers'].update(self.header)
            
            # Execute the request
            response = func(*args, **kwargs)
            
            # If unauthorized, try to refresh token and retry
            if response.status_code == 403:
                max_retries = 5
                n_try = 1
                self.logger.warning(f"Got 403 Unauthorized, attempting to refresh token [{n_try}/{max_retries}]")
                while not self.refresh_token():
                    n_try += 1
                    self.logger.warning(f"Got 403 Unauthorized, attempting to refresh token [{n_try}/{max_retries}]")
                    if n_try > max_retries:
                        raise Exception("Unable to refresh token")

                self.logger.info("Token refreshed successfully, retrying request")
                # Update headers with new token
                if 'headers' not in kwargs:
                    kwargs['headers'] = {}
                kwargs['headers'].update(self.header)
                
                # Retry the request
                return func(*args, **kwargs)

            return response
        return wrapper

