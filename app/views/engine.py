from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc

class EngineModel(object):

    def __init__(self):
        options = Options()
        # options.add_argument('--headless')
        # options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        # options.add_argument('--incognito')
        # options.add_argument("--disable-crash-reporter")
        # options.add_argument("--disable-extensions")
        # options.add_argument("--disable-in-process-stack-traces")
        # options.add_argument("--disable-logging")
        options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--log-level=3")
        # options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.browser = uc.Chrome(driver_executable_path=ChromeDriverManager().install(), options=options)
        self.url = ''
        self.FILENAME = ''

    def get_info(self, url):
        pass
