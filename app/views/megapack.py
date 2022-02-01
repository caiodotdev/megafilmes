from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from app.views.engine import EngineModel


class MegaPack(EngineModel):
    def __init__(self, url=None):
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

    def get_code(self, link_baixar):
        if 'hls1' in link_baixar and 'm3u8' in link_baixar:
            return str(link_baixar.split('hls1/')[1].split('.m3u8')[0])
        return None

    def extract_m3u8(self):
        html = self.browser.page_source
        soup = BeautifulSoup(html, 'html.parser')
        try:
            player = soup.find('div', {'id': 'instructions'}).find('div', {'id': 'RedeCanaisPlayer'})
            if player.has_attr('baixar'):
                link_baixar = player['baixar']
                link_baixar = self.cut_url(link_baixar)
                return {'m3u8': self.create_link(link_baixar), 'code': self.get_code(link_baixar)}
        except (Exception,):
            print('--- Nao encontrou div#instructions')
        return None

    def get_info_sinal_publico(self, url=None):
        if url:
            self.url = url
        self.browser.get(self.url)
        return self.extract_m3u8()

    def close(self):
        self.browser.close()
        self.browser.quit()

    def get_info(self, url=None):
        if url:
            self.url = url
        self.browser.get(self.url)
        frame = self.get_frame(self.browser.find_elements(By.CLASS_NAME, "rptss"))
        if frame:
            self.browser.switch_to.frame(frame)
        else:
            print('Nao encontrou o frame de video.')
        return self.extract_m3u8()

    def cut_url(self, url: str):
        word = 'download.php?vid='
        index = url.index(word) + len(word)
        url = str(url[index:])
        return url
