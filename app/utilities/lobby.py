import requests
from dateutil import parser
import time


class Lobby:
    def __init__(self, url, data):
        self.id = data["id"]
        self.status = None
        self.url = url+"api/collections/lobbies/"
        self.creation_date = parser.isoparse(data["creationDate"]).timestamp()
        self.pre_event_date = parser.isoparse(data["preEventDate"]).timestamp()
        self.event_date = parser.isoparse(data["eventDate"]).timestamp()
        self.post_event_date = parser.isoparse(data["postEventDate"]).timestamp()


    
    def fetch_lobby(self):
        """
        Fetch the lobby data from the server.
        """
        response = requests.get(self.url + self.id)
        if response.status_code == 200:
            return Lobby(self.url, response.json())
        