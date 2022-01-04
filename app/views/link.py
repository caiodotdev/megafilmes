import time
from html import unescape

from bs4 import BeautifulSoup

from app.views.core import EngineModel


class MegaPack(EngineModel):
    def __init__(self, url):
        super(MegaPack, self).__init__()
        self.url = url

    def get_info(self):
        print('Start GET_INFO')
        print('Search in: {}'.format(self.url))
        self.browser.get(self.url)
        self.browser.switch_to.frame(self.browser.find_element_by_class_name("rptss"))
        html = self.browser.page_source
        soup = BeautifulSoup(html, 'html.parser')
        player = soup.find('div', {'id': 'instructions'}).find('div', {'id': 'RedeCanaisPlayer'})
        if player.has_attr('baixar'):
            link_baixar = player['baixar']
            link_baixar = self.cut_url(link_baixar)
            return link_baixar
        self.browser.switch_to.default_content()
        return None

    def cut_url(self, url: str):
        word = 'download.php?vid='
        index = url.index(word) + len(word)
        url = url[index:]
        return url
