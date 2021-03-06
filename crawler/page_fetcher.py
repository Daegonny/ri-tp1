import os
import time
from threading import Thread
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


class PageFetcher(Thread):
    def __init__(self, obj_scheduler):
        self.obj_scheduler = obj_scheduler
        self.finished = False
        Thread.__init__(self)

    def request_url(self, obj_url):
        """
        Faz a requisição e retorna o conteúdo em binário da URL passada como parametro
        obj_url: Instancia da classe ParseResult com a URL a ser requisitada.
        """
        try:
            response = requests.get(obj_url.geturl(),timeout=0.1, headers={
                                    'user-agent': self.obj_scheduler.str_usr_agent})
            if 'text/html' in response.headers['content-type']:
                return response.content
            else:
                return None
        except Exception:
            return None

    def discover_links(self, obj_url, int_depth, bin_str_content):
        """
        Retorna os links do conteúdo bin_str_content da página já requisitada obj_url
        """
        soup = BeautifulSoup(bin_str_content, features="lxml")
        list_url_depth = []
        for link in soup.select('a'):
            try:
                obj_new_url = urlparse(urljoin(obj_url.geturl(), link['href']))
                if(obj_new_url.netloc == obj_url.netloc):
                    int_new_depth = int_depth + 1
                else:
                    int_new_depth = 0
                list_url_depth.append((obj_new_url, int_new_depth))
            except:
                pass
        return list_url_depth

    def crawl_new_url(self):
        """
        Coleta uma nova URL, obtendo-a do escalonador.
        Se nenhum domínio estiver disponível aguarda.
        Se página puder ser acessada faz sua requisição.
        Se puder ser coletada envia URL pro escalonador salvar.
        Se puder coletar os links, envia para o escalonador gerenciar.
        """
        url, depth, time_to_wait = self.obj_scheduler.get_next_url()

        while time_to_wait and not self.obj_scheduler.has_finished_crawl():
            time.sleep(time_to_wait)
            url, depth, time_to_wait = self.obj_scheduler.get_next_url()

        if(url == None):
            self.finished = True
            return

        can_fetch_page = self.obj_scheduler.can_fetch_page(url)
     
        if(url != None and not self.obj_scheduler.has_finished_crawl() and can_fetch_page):
            response = self.request_url(url)
            if response:
                if not self.has_no_index(response):
                    self.collect(url)

                if not self.has_no_follow(response):
                    self.gather_links(url, depth, response)

    
    def collect(self, obj_url):
        """
        Envia URL coletada para o escalonador gerenciar.
        """
        self.obj_scheduler.collect_url(obj_url)

    def gather_links(self, obj_url, depth, response_content):
        """
        Dado um response devolve as URLS contidas nele
        """
        links = self.discover_links(obj_url, depth, response_content)
        for (new_url, new_depth) in links:
            if(new_url.geturl()):
                self.obj_scheduler.add_new_page(new_url, new_depth)

    def has_no_index(self, response_content):
        """
        retorna se a página contém tag no index
        """
        return self.check_meta_content(response_content, 'noindex')

    def has_no_follow(self, response_content):
        """
        retorna se a página contém tag no follow
        """
        return self.check_meta_content(response_content, 'nofollow')

    def check_meta_content(self, response_content, keyword):
        """
        verifica se a página contém uma tag específica no meta content
        """
        flag = False
        if response_content:
            soup = BeautifulSoup(response_content, features="lxml")
            for meta in soup.find_all('meta', attrs={'name': 'robots'}):
                try:
                    if (keyword in meta['content']):
                        flag = True
                        break
                except:
                    pass
            return flag
        return flag

    def run(self):
        """
        Executa coleta enquanto houver páginas a serem coletadas
        """
        while not self.obj_scheduler.has_finished_crawl() and not self.finished:
            self.crawl_new_url()