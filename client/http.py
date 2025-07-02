import requests


class Http:
    def __init__(self):
        self.__session = requests.Session()
        self.__headers = {}

    @property
    def headers(self):
        return self.__headers

    @property
    def cookies(self):
        return self.__session.cookies

    def get(self, url: str) -> str:
        return self.__session.get(url, headers=self.__headers).text
