import logging

from django.conf import settings
from django.test import LiveServerTestCase
from selenium import webdriver

BROWSERSTACK_USERNAME = settings.BROWSERSTACK_USERNAME
BROWSERSTACK_ACCESSKEY = settings.BROWSERSTACK_ACCESSKEY

class BaseSeleniumTestCase(LiveServerTestCase):
    port = 8000

    logger = None

    def setUp(self):
        super(BaseSeleniumTestCase, self).setUp()
        print('----- Remoto')
        desired_cap = {
            'os_version': '11',
            'resolution': '1920x1080',
            'browser': 'Chrome',
            'browser_version': 'latest',
            'os': 'Windows',
            }
        self.driver = webdriver.Remote(
            command_executor='https://caiodotdev_irwadE:Ke15XkyiQ6qp9XryA26w@hub-cloud.browserstack.com/wd/hub',
            desired_capabilities=desired_cap)

    def tearDown(self) -> None:
        self.driver.quit()
        super(BaseSeleniumTestCase, self).tearDown()

    def get(self, url):
        self.driver.get(url)
        self.driver.set_window_size(1920, 1200)
