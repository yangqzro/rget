import requests


class Http:
    def __init__(self):
        self._session = requests.Session()

    def get(self, url: str) -> str:
        return self._session.get(url).text
