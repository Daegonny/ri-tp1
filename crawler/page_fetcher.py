from bs4 import BeautifulSoup
from threading import Thread
import requests
from urllib.parse import urlparse,urljoin

class PageFetcher(Thread):
    def __init__(self, obj_scheduler):
        self.obj_scheduler = obj_scheduler
        self.finished = False
        Thread.__init__(self)


    def request_url(self,obj_url):
        """
            Faz a requisição e retorna o conteúdo em binário da URL passada como parametro

            obj_url: Instancia da classe ParseResult com a URL a ser requisitada.
        """
        response = requests.get(obj_url.geturl(),headers = {'user-agent': self.obj_scheduler.str_usr_agent})
        if 'text/html' in response.headers['content-type']:
            return response.content
        else:
            return None        

    def discover_links(self,obj_url,int_depth,bin_str_content):
        """
        Retorna os links do conteúdo bin_str_content da página já requisitada obj_url
        """
        soup = BeautifulSoup(bin_str_content,features="lxml")
        for link in soup.select('a'):
            try:
                obj_new_url = urlparse(urljoin(obj_url.geturl(), link['href']))
                int_new_depth = int_depth + 1
                yield obj_new_url,int_new_depth
            except:
                pass

    def crawl_new_url(self):
        """
            Coleta uma nova URL, obtendo-a do escalonador
        """
        url, depth = self.obj_scheduler.get_next_url()
        
        if(url == None):
            self.finished = True
            return
        
        response = self.request_url(url)
        if(url != None and not self.obj_scheduler.has_finished_crawl()):
            self.obj_scheduler.collect_url(url)
            print(url.geturl())
            self.obj_scheduler.count_fetched_page()
            links = self.discover_links(url, depth, response)
            for (new_url, new_depth) in links:
                self.obj_scheduler.add_new_page(new_url, new_depth)


    def run(self):
        """
            Executa coleta enquanto houver páginas a serem coletadas
        """
        while not self.obj_scheduler.has_finished_crawl() and not self.finished:
            self.crawl_new_url()