import logging
import requests
from bs4 import BeautifulSoup
from pyppeteer import launch
import asyncio
import nest_asyncio
import pandas as pd
from joblib import Parallel, delayed
from time import time
from datetime import datetime

from config_file import configs


def get_logger():

    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Set the minimum log level

    # Create a file handler for output file
    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.DEBUG)
    # Create a console handler for output to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Create a formatter and set it for both handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
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
        self.language = config.get("language", "")
        self.base_url = config.get("base_url", "")
        self.language = config.get("language", "")
        self.target_categories = config.get("target_categories", [])

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

    def fetch_content_in_news(self, url):
        headline_identifier = self.headline_identifier
        datetime_identifier = self.datetime_identifier
        content_identifier = self.content_identifier

        with requests.get(url, headers=self.headers) as r:
            soup = BeautifulSoup(r.content, "lxml")
            if self.is_debug:
                print("Status code :", r.status_code, "| url :", url)

        data_dict = {
            "platform": self.name,
            "language": self.language,
            "headline": soup.select_one(headline_identifier).text.strip(),
            "datetime": soup.select_one(datetime_identifier).text.strip(),
            "scrapetime": datetime.now().strftime("%Y%m%d %H:%M"),
            "url": url,
            "content": soup.select_one(content_identifier).text.strip().replace("\n", " ")
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

    def get_category_urls(self):
        category_urls = [self.base_url + path for path in self.target_categories]
        return category_urls

    def start_scraping(self):
        category_urls = self.get_category_urls()
        logger.info("Category URLs : ")
        logger.info(category_urls)

        data_dict_list = []
        for category_url in category_urls:
            logger.info("Fetching all news links ... " + category_url)
            news_urls = self.fetch_links_in_category(category_url)
            news_urls = list(set(news_urls))
            logger.info("Total news links : " + f"{len(news_urls)}")

            logger.info("Fetching each news content ...")
            for news_url in news_urls:
                try:
                    logger.info("Fetching " + news_url)
                    data_dict_list.append(self.fetch_content_in_news(news_url))
                except Exception as e:
                    logger.error(e)

        return data_dict_list


def export_data(news_dict_list):
    df = pd.DataFrame(news_dict_list)
    df.to_csv(f"data/news_data_utf8.csv", sep="\t", index=False, encoding="utf-8")
    df.to_csv(f"data/news_data.csv", sep="\t", index=False)
    logger.info("Export data files success!!!")


@timer_func
def main():
    news_dict_list = []
    for config in configs:
        logger.info(f"************   {config['name']}   ************")

        webscraper = WebScraper(config)
        data_dict_list = webscraper.start_scraping()
        if len(data_dict_list) == 0:
            logger.info(f"************   {config['name']} fail to fetch data")
            continue
        news_dict_list += data_dict_list

    export_data(news_dict_list)


logger = get_logger()


if __name__ == '__main__':
    main()



