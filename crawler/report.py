import matplotlib.pyplot as plt

from .page_fetcher import PageFetcher
from .scheduler import Scheduler
from .utils import get_arr_str_urls_seeds_from_seeds_file


class Report:
    def init_scheduler(self, int_page_limit=30, int_depth_limit=6):
        arr_str_urls_seeds = get_arr_str_urls_seeds_from_seeds_file()

        scheduler = Scheduler(str_usr_agent="ri2020g3bot (https://daegonny.github.io/ri-tp1/)",
                              int_page_limit=int_page_limit,
                              int_depth_limit=int_depth_limit,
                              arr_urls_seeds=arr_str_urls_seeds)
        return scheduler

    def run_crawler(self, int_page_limit=30, int_depth_limit=6, n_threads=10):
        scheduler = self.init_scheduler(
            int_page_limit=int_page_limit, int_depth_limit=int_depth_limit)
        fetchers = []
        for _ in range(n_threads):
            fetcher = PageFetcher(scheduler)
            fetcher.start()
            fetchers.append(fetcher)

        for fetcher in fetchers:
           fetcher.join()
        #scheduler.save_collected_urls()

    def plot(self, data, title):
        names = list(data.keys())
        values = list(data.values())
        fig, ax = plt.subplots()
        ax.scatter(names, values)
        fig.suptitle(title)

    def velocity_result(self, int_page_limit=30, int_depth_limit=6):
        results = {}
        for n_threads in range(10, 110, 20):
            scheduler = self.init_scheduler(
                int_page_limit=int_page_limit, int_depth_limit=int_depth_limit)
            fetchers = []

            for _ in range(n_threads):
                fetcher = PageFetcher(scheduler)
                fetcher.start()
                fetchers.append(fetcher)

            for fetcher in fetchers:
                fetcher.join()

            results.update({n_threads: scheduler.crawl_duration.seconds})
        self.plot(data=results, title='Análise de velocidade')
