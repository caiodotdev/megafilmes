from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from app.views.engine import EngineModel


class MegaPack(EngineModel):
    def __init__(self, url):
        super(MegaPack, self).__init__()
        self.url = url

    def get_frame(self, list):
        NOT_ALLOWED = ['youtube']
        for iframe in list:
            src = iframe.get_attribute('src')
            if not any(domain in src for domain in NOT_ALLOWED):
                return iframe
        return None

    def create_link(self, text):
        if 'http' not in text:
            return 'http://' + text
        return text

    def get_info(self):
        self.browser.get(self.url)
        frame = self.get_frame(self.browser.find_elements(By.CLASS_NAME, "rptss"))
        if frame:
            self.browser.switch_to.frame(frame)
        else:
            print('Nao encontrou o frame de video.')
        html = self.browser.page_source
        soup = BeautifulSoup(html, 'html.parser')
        try:
            player = soup.find('div', {'id': 'instructions'}).find('div', {'id': 'RedeCanaisPlayer'})
            if player.has_attr('baixar'):
                link_baixar = player['baixar']
                link_baixar = self.cut_url(link_baixar)
                self.browser.close()
                self.browser.quit()
                return self.create_link(link_baixar)
        except (Exception,):
            self.browser.close()
            self.browser.quit()
            print('--- Nao encontrou div#instructions')
        return None

    def cut_url(self, url: str):
        word = 'download.php?vid='
        index = url.index(word) + len(word)
        url = str(url[index:])
        return url
