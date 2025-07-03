from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class ChromeBrowser:
    @staticmethod
    def open(url: str, options: webdriver.ChromeOptions):
        return ChromeBrowser(url, options)

    def __init__(self, url: str, options: webdriver.ChromeOptions = None):
        self.__url = url
        self.__driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.__driver.get(self.__url)

    def get_cookies(self) -> dict:
        return {cookie.get("name"): cookie.get("value") for cookie in self.__driver.get_cookies()}

    def get_cookie(self, name: str) -> dict:
        return self.__driver.get_cookie(name).get("value")

    def execute_script(self, script: str) -> str:
        return self.__driver.execute_script(script)

    def quit(self):
        self.__driver.quit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.quit()

    def __del__(self) -> None:
        self.quit()
