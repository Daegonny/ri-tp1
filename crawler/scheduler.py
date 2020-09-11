from urllib import robotparser
from util.threads import synchronized
from collections import OrderedDict
from .domain import Domain

class Scheduler():
    #tempo (em segundos) entre as requisições
    TIME_LIMIT_BETWEEN_REQUESTS = 20

    def __init__(self,str_usr_agent,int_page_limit,int_depth_limit,arr_urls_seeds):
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

        self.dic_url_per_domain = OrderedDict()
        self.set_discovered_urls = set()
        self.dic_robots_per_domain = {}


    @synchronized
    def count_fetched_page(self):
        """
            Contabiliza o número de paginas já coletadas
        """
        self.int_page_count += 1

    def has_finished_crawl(self):
        """
            Verifica se finalizou a coleta
        """
        if(self.int_page_count > self.int_page_limit):
            return True
        return False


    @synchronized
    def can_add_page(self,obj_url,int_depth):
        """
            Retorna verdadeiro caso  profundade for menor que a maxima
            e a url não foi descoberta ainda
        """
        return int_depth < self.int_depth_limit and (not obj_url in self.set_discovered_urls)

    @synchronized
    def add_new_page(self,obj_url,int_depth):
        """
            Adiciona uma nova página
            obj_url: Objeto da classe ParseResult com a URL a ser adicionada
            int_depth: Profundidade na qual foi coletada essa URL
        """
        #https://docs.python.org/3/library/urllib.parse.html
        if(self.can_add_page(obj_url, int_depth)):
            
            domain = Domain(obj_url.netloc, self.TIME_LIMIT_BETWEEN_REQUESTS)
            
            if not domain.nam_domain in self.dic_url_per_domain:
                self.dic_url_per_domain[domain] = []
            
            self.dic_url_per_domain[domain.nam_domain].append((obj_url, int_depth))
        
            self.set_discovered_urls.add(obj_url)
            return True
        
        return False


    @synchronized
    def get_next_url(self):
        """
        Obtem uma nova URL por meio da fila. Essa URL é removida da fila.
        Logo após, caso o servidor não tenha mais URLs, o mesmo também é removido.
        """
        
        url = depth = None 
        domains_to_remove = []
        while(url == None and depth == None and len(self.dic_url_per_domain) > 0):
            for domain, urls in  self.dic_url_per_domain.items():
                if domain.is_accessible():
                    domain.accessed_now()
                    if len(urls) > 0:
                        url, depth = urls[0]
                        urls.remove((url, depth))
                        break
                    else:
                        domains_to_remove.append(domain)
                   
        
        for domain in domains_to_remove:
            self.dic_url_per_domain.pop(domain, None)
            
        return  url, depth

    def can_fetch_page(self,obj_url):
        """
        Verifica, por meio do robots.txt se uma determinada URL pode ser coletada
        """



        return False
