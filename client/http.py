import requests


class Http:
    def __init__(self, base_uri: str = "", options: dict = {}):
        self.__base_uri = base_uri
        self.__session = requests.Session()
        self.__headers = {}
        self.__options = options
        self.__timeout = 5

    @property
    def headers(self):
        return self.__headers

    @property
    def cookies(self):
        return self.__session.cookies

    def get(self, api: str, **kwargs):
        url, headers = self.__base_uri + api, self.headers
        if self.__options.get("auto_referer"):
            headers = {"Referer": url, **headers}
        return self.__session.get(url, headers=headers, timeout=self.__timeout, **kwargs)

    def post(self, api: str, data: dict = None, json: dict = None, **kwargs):
        url, headers = self.__base_uri + api, self.headers
        if self.__options.get("auto_referer"):
            headers = {"Referer": url, **headers}
        return self.__session.post(url, headers=headers, data=data, json=json, timeout=self.__timeout, **kwargs)
