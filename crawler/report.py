import matplotlib.pyplot as plt
from tqdm import tqdm

from .page_fetcher import PageFetcher
from .scheduler import Scheduler
from .utils import get_arr_str_urls_seeds_from_seeds_file


class Report:
    def init_scheduler(self):
        arr_str_urls_seeds = get_arr_str_urls_seeds_from_seeds_file()

        scheduler = Scheduler(str_usr_agent="ri2020g3bot (https://daegonny.github.io/ri-tp1/)",
                              int_page_limit=30,
                              int_depth_limit=3,
                              arr_urls_seeds=arr_str_urls_seeds)
        return scheduler

    def plot(self, data, title):
        names = list(data.keys())
        values = list(data.values())
        fig, ax = plt.subplots()
        ax.scatter(names, values)
        fig.suptitle(title)

    def velocity_result(self):
        results = {}
        for n_threads in tqdm(range(10, 110, 20)):
            scheduler = self.init_scheduler()
            fetchers = []

            for _ in range(n_threads):
                fetcher = PageFetcher(scheduler)
                fetcher.start()
                fetchers.append(fetcher)

            for fetcher in fetchers:
                fetcher.join()

            results.update({n_threads: scheduler.crawl_duration.seconds})
        self.plot(data=results, title='Análise de velocidade')
