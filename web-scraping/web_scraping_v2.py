import random
import logging
import re
import requests
from bs4 import BeautifulSoup
from pyppeteer import launch
import asyncio
from pymongo import MongoClient
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
        file_handler = logging.FileHandler('web_scraping_v2.log')
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

        self.num_scroll = config.get("num_scroll", 2)
        self.news_card_identifier = config.get("news_card_identifier", "")
        self.headline_identifier = config.get("headline_identifier", "")
        self.datetime_identifier = config.get("datetime_identifier", "")
        self.content_identifier = config.get("content_identifier", "")

        self.is_debug = config.get("is_debug", False)

    def fetch_links_in_category(self, url):
        news_card_identifier = self.news_card_identifier

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

        # Use re.sub to replace multiple spaces with a single space
        content = soup.select_one(content_identifier)
        if content is None or len(content.text.strip()) == 0:
            return None
        content = re.sub(r'\s+', ' ', content.text.strip())

        scrape_time = datetime.now()
        news_datetime = soup.select_one(datetime_identifier)
        if news_datetime:
            news_datetime = news_datetime.get("datetime", news_datetime.text.strip())

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

    async def scroll_and_scrape(self, url, num_scroll=2, timeout=30000):
        browser = None
        try:
            browser = await launch(headless=True, args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--no-zygote',
                '--single-process',
            ])
            page = await browser.newPage()
            await page.setUserAgent(self.headers['User-Agent'])

            logger.info(f"[Async scroll_and_scrpae] Navigating to {url}")
            await page.goto(url, {"timeout": timeout})

            # Scroll down the page
            for _ in range(num_scroll):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight);')
                await asyncio.sleep(2)  # Wait for content to load

            content = await page.content()
            logger.info(f"Successfully scraped content from {url}")

            return content

        except Exception as e:
            logger.error(f"Error while scraping Categories {url}: {e}")
            return None

        finally:
            if browser:
                await browser.close()

    def _remove_existing_urls(self, news_urls, existing_urls):
        return list(set(news_urls) - existing_urls)

    def _remove_duplicated_urls(self, all_news_urls_with_categories):
        existing_urls = set(get_urls_from_db(self.name))
        unique_news_urls_with_categories = []
        seen_urls = set()

        for url, category in all_news_urls_with_categories:
            if url not in seen_urls and url not in existing_urls:
                seen_urls.add(url)
                unique_news_urls_with_categories.append((url, category))

        return unique_news_urls_with_categories

    def get_category_urls(self):
        category_urls = [self.base_url + path for path in self.target_categories]
        return category_urls

    def start_scraping(self):
        category_urls = self.get_category_urls()
        categories = self.categories
        logger.info("Category URLs : ")
        logger.info(category_urls)

        all_news_urls_with_categories = []
        for category_url, category in zip(category_urls, categories):
            logger.info("Fetching all news links ... " + category_url)
            try:
                news_urls = self.fetch_links_in_category(category_url)
                all_news_urls_with_categories.extend((url, category) for url in news_urls)
            except Exception as e:
                logger.error(e)

        news_urls_categories = self._remove_duplicated_urls(all_news_urls_with_categories)

        logger.info(f"Fetching each news content ... for Total {len(news_urls_categories)} links ...")
        data_dict_list = []
        for news_url, category in news_urls_categories:
            try:
                data_dict = self.fetch_content_in_news(news_url, category)
                if data_dict is not None:
                    data_dict_list.append(data_dict)
            except Exception as e:
                logger.error(e)

        logger.info("Successfully fetched all categories!")
        return data_dict_list


def format_job_log_data(total_articles, data_stats, dt1, dt2, num_cores):
    t_seconds = (dt2 - dt1).total_seconds()
    t_minutes = t_seconds / 60

    job_log_data = {
        "start_time": dt1.strftime('%Y-%m-%d %H:%M'),
        "end_time": dt2.strftime('%Y-%m-%d %H:%M'),
        "num_cores": num_cores,
        "time_spent": f"{t_seconds:.2f} s ({t_minutes:.2f} mins)",
        "total_articles": total_articles,
        "data_stats": data_stats
    }
    return job_log_data


def save_job_log_to_db(job_log_data):
    try:
        job_log_collection.insert_one(job_log_data)
    except Exception as e:
        logger.error("Error saving job log to db")
        logger.error(e)


def save_data_to_db(news_dict_list):
    try:
        result = news_data_collection.insert_many(news_dict_list)
        logger.info(f"Inserted IDs: {result.inserted_ids}")
    except Exception as e:
        logger.error("Error saving news data to db")
        logger.error(e)


def get_urls_from_db(platform):
    try:
        existing_urls = news_data_collection.find(
            {"platform": platform},
            {"url": 1, "_id": 0}  # Only fetch the 'url' field
        )
        return {doc['url'] for doc in existing_urls}
    except Exception as e:
        logger.error("Error getting existing urls from db")
        logger.error(e)
        return set()


def scrape_one(config):
    webscraper = WebScraper(config)
    data_dict_list = webscraper.start_scraping()
    if len(data_dict_list) == 0:
        logger.info(f"************   {config['name']} fail to fetch data, len(data_dict_list) == 0")
        return []

    return data_dict_list


def main(num_cores=1):
    data_stats = {}
    total_articles = 0
    t1 = time()
    dt1 = datetime.now()

    random.shuffle(configs)
    for config in configs:
        logger.info(f"************************   Start Fetching {config['name']}   ************************")
        data_dict_list = scrape_one(config)
        data_stats[config['name']] = len(data_dict_list)
        total_articles += len(data_dict_list)
        save_data_to_db(data_dict_list)
        data_dict_list = [] # clean the items in list to reduce memory requirement

    t2 = time()
    dt2 = datetime.now()
    job_log_data = format_job_log_data(total_articles, data_stats, dt1, dt2, num_cores)
    save_job_log_to_db(job_log_data)
    logger.info(f"Total time spent: {t2-t1:.4f} s")


logger = get_logger(is_file=False, is_console=True)


if __name__ == '__main__':
    t = datetime.now().strftime('%Y-%m-%d %H:%M')
    logger.info("***************************************************")
    logger.info(f"************** {t} *******************")
    logger.info("***************************************************")

    main()
