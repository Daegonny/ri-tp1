import os
import time
from collections import OrderedDict
from datetime import datetime, timedelta
from urllib import robotparser

from util.threads import synchronized

from .domain import Domain


class Scheduler():
    # tempo (em segundos) entre as requisições
    TIME_LIMIT_BETWEEN_REQUESTS = 30

    def __init__(self, str_usr_agent, int_page_limit, int_depth_limit, arr_urls_seeds):
        """
            Inicializa o escalonador. Atributos:
                - `str_usr_agent`: Nome do `User agent`. Usualmente, é o nome do navegador, em nosso caso,  será o nome do coletor (usualmente, terminado em `bot`)
                - `int_page_limit`: Número de páginas a serem coletadas
                - `int_depth_limit`: Profundidade máxima a ser coletada
                - `int_page_count`: Quantidade de página já coletada
                - `dic_url_per_domain`: Fila de URLs por domínio (explicado anteriormente)
                - `set_discovered_urls`: Conjunto de URLs descobertas, ou seja, que foi extraída em algum HTML e já adicionadas na fila - mesmo se já ela foi retirada da fila. A URL armazenada deve ser uma string.
                - `dic_robots_per_domain`: Dicionário armazenando, para cada domínio, o objeto representando as regras obtidas no `robots.txt`
        """
        self.str_usr_agent = str_usr_agent
        self.int_page_limit = int_page_limit
        self.int_depth_limit = int_depth_limit
        self.int_page_count = 0
        self.start_time = datetime.now()
        self.dic_url_per_domain = OrderedDict()
        self.set_discovered_urls = set()
        self.dic_robots_per_domain = {}
        self.finished = False
        self.list_collected_urls = []
        self.crawl_duration = None
        self.collected_urls_file_name = 'crawler/urls.txt'
        self.remove_collected_urls_file()
        
        [self.add_new_page(url, 0) for url in arr_urls_seeds]

    def remove_collected_urls_file(self):
        try:
            os.remove(self.collected_urls_file_name)
        except FileNotFoundError:
            pass

    @synchronized
    def count_fetched_page(self):
        """
            Contabiliza o número de paginas já coletadas
        """
        self.int_page_count += 1
        if(self.int_page_count > self.int_page_limit):
            if(not self.finished):
                self.crawl_duration = datetime.now() - self.start_time
                print(f"Finished with {str(self.crawl_duration)}")
            self.finished = True

    @synchronized
    def has_finished_crawl(self):
        """
            Verifica se finalizou a coleta
        """
        return self.finished

    @synchronized
    def can_add_page(self, obj_url, int_depth):
        """
            Retorna verdadeiro caso  profundade for menor que a maxima
            e a url não foi descoberta ainda
        """
        return int_depth < self.int_depth_limit and (not obj_url in self.set_discovered_urls)

    @synchronized
    def add_new_page(self, obj_url, int_depth):
        """
            Adiciona uma nova página
            obj_url: Objeto da classe ParseResult com a URL a ser adicionada
            int_depth: Profundidade na qual foi coletada essa URL
        """
        # https://docs.python.org/3/library/urllib.parse.html
        if(self.can_add_page(obj_url, int_depth)):
            domain = Domain(obj_url.netloc, self.TIME_LIMIT_BETWEEN_REQUESTS)

            if not domain.nam_domain in self.dic_url_per_domain:
                self.dic_url_per_domain[domain] = []

            self.dic_url_per_domain[domain.nam_domain].append(
                (obj_url, int_depth))

            self.set_discovered_urls.add(obj_url)
            return True

        return False

    @synchronized
    def get_next_url(self):
        """
        Obtem uma nova URL por meio da fila. Essa URL é removida da fila.
        Logo após, caso o servidor não tenha mais URLs, o mesmo também é removido.
        """
        url = depth = time_to_wait = min_time_to_wait = None
        domains_to_remove = []

        if(len(self.dic_url_per_domain) > 0 and not self.finished):

            for domain, urls in self.dic_url_per_domain.items():
                if domain.is_accessible():
                    if len(urls) > 0:
                        domain.accessed_now()
                        url, depth = urls[0]
                        urls.remove((url, depth))
                        break
                    else:
                        domains_to_remove.append(domain.nam_domain)

                elif(min_time_to_wait == None or min_time_to_wait > domain.time_will_be_acessible):
                    min_time_to_wait = domain.time_will_be_acessible

            for domain in domains_to_remove:
                #print("removed", domain)
                self.dic_url_per_domain.pop(domain)
                
            if(url == None and depth == None):
                time_to_wait = max((min_time_to_wait - datetime.now()).total_seconds(), 0) if min_time_to_wait else 0

        return url, depth, time_to_wait

    def get_robots(self, nam_domain):
        """
        retorna o robots de um domínio
        """
        robot_parser = robotparser.RobotFileParser()
        robot_parser.set_url(f"http://{nam_domain}/robots.txt")
        robot_parser.read()
        return robot_parser

    @synchronized
    def can_fetch_page(self, obj_url):
        """
        Verifica, por meio do robots.txt se uma determinada URL pode ser coletada
        """
        url = obj_url.geturl()
        domain = obj_url.netloc
        if domain not in self.dic_robots_per_domain:
            try:
                self.dic_robots_per_domain[domain] = self.get_robots(
                    domain).can_fetch(self.str_usr_agent, url)
            except:
                self.dic_robots_per_domain[domain] = False
                return False
        return self.dic_robots_per_domain.get(domain)

    @synchronized
    def collect_url(self, obj_url):
        #print("collected", obj_url.geturl())
        self.count_fetched_page()
        self.list_collected_urls.append(obj_url.geturl())
        
    def save_collected_urls(self):
        with open(self.collected_urls_file_name, 'a') as collected_file:
            for url in self.list_collected_urls:
                print(url, file=collected_file)
