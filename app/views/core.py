from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class EngineModel(object):

    def __init__(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--disable-gpu')
        options.add_argument('--incognito')
        self.browser = webdriver.Chrome(options=options)
        self.url = ''
        self.FILENAME = ''

    def get_info(self):
        pass
