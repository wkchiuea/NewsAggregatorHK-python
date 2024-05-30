import argparse
import logging
import re
import requests
from bs4 import BeautifulSoup
from pyppeteer import launch
import asyncio
from pymongo import MongoClient
from joblib import Parallel, delayed
from time import time
from datetime import datetime

from config_file import configs




client = MongoClient('mongodb://localhost:27017/')
db = client['raw_news']
news_data_collection = db['news_data']
job_log_collection = db['job_log']


def get_logger(is_file=False, is_console=False):

    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Set the minimum log level

    # Create a formatter and set it for both handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')

    if is_file:
        # Create a file handler for output file
        file_handler = logging.FileHandler('app.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if is_console:
        # Create a console handler for output to console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def timer_func(func):
    def wrap_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print(f'Function {func.__name__!r} executed in {(t2-t1):.4f}s')
        return result
    return wrap_func


class WebScraper:

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    def __init__(self, config):
        self.name = config.get("name", "")
        self.name_zh = config.get("name_zh", "")
        self.name_en = config.get("name_en", "")
        self.language = config.get("language", "")
        self.base_url = config.get("base_url", "")
        self.language = config.get("language", "")
        self.target_categories = config.get("target_categories", [])
        self.categories = config.get("categories", [])

        self.existing_urls = config.get("existing_urls", set())

        self.num_scroll = config.get("num_scroll", 2)
        self.news_card_identifier = config.get("news_card_identifier", "")
        self.headline_identifier = config.get("headline_identifier", "")
        self.datetime_identifier = config.get("datetime_identifier", "")
        self.content_identifier = config.get("content_identifier", "")

        self.is_debug = config.get("is_debug", False)

    def fetch_links_in_category(self, url):
        news_card_identifier = self.news_card_identifier

        with requests.get(url, headers=self.headers) as r:
            soup = BeautifulSoup(r.content, "lxml")
            if self.is_debug:
                print("status code :", r.status_code)

        content = asyncio.get_event_loop().run_until_complete(self.scroll_and_scrape(url, num_scroll=self.num_scroll))
        soup = BeautifulSoup(content, "lxml")

        cards = soup.select(news_card_identifier)
        news_urls = [card.find("a").attrs["href"] if card.find("a") else card.attrs.get("href", "") for card in cards]
        news_urls = [url.split("#")[0] for url in news_urls if len(url) > 0]
        news_urls = self.format_urls_to_absolute_urls(news_urls)

        return news_urls

    def fetch_content_in_news(self, url, category):
        headline_identifier = self.headline_identifier
        datetime_identifier = self.datetime_identifier
        content_identifier = self.content_identifier

        with requests.get(url, headers=self.headers) as r:
            soup = BeautifulSoup(r.content, "lxml")
            if self.is_debug:
                print("Status code :", r.status_code, "| url :", url)

        scrape_time = datetime.now()
        news_datetime = soup.select_one(datetime_identifier)
        if news_datetime:
            news_datetime = news_datetime.get("datetime", news_datetime.text.strip())

        # Use re.sub to replace multiple spaces with a single space
        content = soup.select_one(content_identifier).text.strip()
        content = re.sub(r'\s+', ' ', content)

        headline = soup.select_one(headline_identifier).text.strip()

        data_dict = {
            "platform": self.name,
            "name_zh": self.name_zh,
            "name_en": self.name_en,
            "language": self.language,
            "category": category,
            "headline": headline,
            "datetime": news_datetime,
            "scrapetime": scrape_time,
            "url": url,
            "content": content
        }

        return data_dict

    async def scroll_and_scrape(self, url, num_scroll=3):
        browser = await launch()
        page = await browser.newPage()
        await page.setUserAgent(self.headers['User-Agent'])
        await page.goto(url, {"timeout": 60000})

        # Scroll down the page
        for _ in range(num_scroll):
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight);')
            await asyncio.sleep(2)  # Wait for content to load

        # Scrape the content
        content = await page.content()

        await browser.close()

        return content

    def format_urls_to_absolute_urls(self, urls):
        base_url = self.base_url

        abs_urls = []
        for url in urls:
            if url.startswith("http"):
                abs_urls.append(url)
            elif not url.startswith("/"):
                abs_urls.append(base_url + url)
            else:
                abs_urls.append(base_url + url[1:])

        return abs_urls

    def _remove_existing_urls(self, news_urls, existing_urls):
        return list(set(news_urls) - existing_urls)

    def get_category_urls(self):
        category_urls = [self.base_url + path for path in self.target_categories]
        return category_urls

    def start_scraping(self):
        category_urls = self.get_category_urls()
        categories = self.categories
        logger.info("Category URLs : ")
        logger.info(category_urls)

        data_dict_list = []
        for category_url, category in zip(category_urls, categories):
            logger.info("Fetching all news links ... " + category_url)
            news_urls = []
            try:
                news_urls = self.fetch_links_in_category(category_url)
                news_urls = self._remove_existing_urls(news_urls, self.existing_urls)
            except Exception as e:
                logger.error(e)
            logger.info("Total news links : " + f"{len(news_urls)}")

            logger.info("Fetching each news content ...")
            for news_url in news_urls:
                try:
                    logger.info("Fetching " + news_url)
                    data_dict_list.append(self.fetch_content_in_news(news_url, category))
                except Exception as e:
                    logger.error(e)

        return data_dict_list


def format_job_log_data(news_dict_list, data_stats, dt1, dt2, num_cores):
    job_log_data = {
        "start_time": dt1.strftime('%Y-%m-%d %H:%M'),
        "end_time": dt2.strftime('%Y-%m-%d %H:%M'),
        "num_cores": num_cores,
        "time_spent": (dt2 - dt1).total_seconds(),
        "total_articles": len(news_dict_list),
        "data_stats": data_stats
    }
    return job_log_data


def save_job_log_to_db(job_log_data):
    try:
        job_log_collection.insert_one(job_log_data)
    except Exception as e:
        logger.error(e)


def save_data_to_db(news_dict_list):
    try:
        result = news_data_collection.insert_many(news_dict_list)
        print(f"Inserted IDs: {result.inserted_ids}")
    except Exception as e:
        logger.error(e)


def get_urls_from_db(platform):
    try:
        existing_urls = news_data_collection.find(
            {"platform": platform},
            {"url": 1, "_id": 0}  # Only fetch the 'url' field
        )
        return {doc['url'] for doc in existing_urls}
    except Exception as e:
        logging.error(e)
        return set()


def add_existing_urls_to_config(_configs):
    for config in _configs:
        config['existing_urls'] = get_urls_from_db(config['name'])
    return _configs


def scrape_one(config):
    webscraper = WebScraper(config)
    data_dict_list = webscraper.start_scraping()
    if len(data_dict_list) == 0:
        logger.info(f"************   {config['name']} fail to fetch data")
        return []

    return data_dict_list


def main(num_cores = 1):
    data_stats = {}
    news_dict_list = []
    t1 = time()
    dt1 = datetime.now()

    configs_ = add_existing_urls_to_config(configs)
    results = Parallel(n_jobs=num_cores)(delayed(scrape_one)(config) for config in configs_)

    for config in configs_:
        logger.info(f"************   {config['name']}   ************")
        data_dict_list = scrape_one(config)
        data_stats[config['name']] = len(data_dict_list)
        news_dict_list += data_dict_list

    t2 = time()
    dt2 = datetime.now()
    job_log_data = format_job_log_data(news_dict_list, data_stats, dt1, dt2, num_cores)
    save_job_log_to_db(job_log_data)
    save_data_to_db(news_dict_list)
    print(f"Total time spent: {t2-t1:.4f} s")


logger = get_logger(is_file=False, is_console=True)


if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run the web scraping script with specified number of cores.")
    parser.add_argument('num_core', type=int, nargs='?', default=1,
                        help='Number of cores to use for parallel processing (default: 1)')

    args = parser.parse_args()

    main()
