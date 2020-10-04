from urllib.parse import urlparse


def get_arr_str_urls_seeds_from_seeds_file():
    arr_str_urls_seeds = []

    with open('crawler/seeds.txt', 'r') as seeds_file:
        for seed_url in seeds_file:
            arr_str_urls_seeds.append(urlparse(seed_url.replace('\n', '')))
    return arr_str_urls_seeds
