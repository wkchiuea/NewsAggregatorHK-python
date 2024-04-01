import requests
from bs4 import BeautifulSoup
from pyppeteer import launch
import asyncio
import nest_asyncio
import pandas as pd


class WebScraper:

    def __init__(self, config):
        self.base_url = config.get("base_url", "")
        self.language = config.get("language", "")
        self.category_str = config.get("category_str", "")
        self.target_categories = config.get("target_categories", "")

        self.num_scroll = config.get("num_scroll", 3)
        self.news_card_identifier = config.get("news_card_identifier", "")

        self.content_identifier_dict = config.get("content_identifier_dict", {})

        self.is_debug = config.get("is_debug", False)

    def fetch_navbar(self):
        base_url = self.base_url
        category_str = self.category_str
        target_categories = self.target_categories

        with requests.get(base_url) as r:
            soup = BeautifulSoup(r.content, "lxml")
            if self.is_debug:
                print("Status code :", r.status_code)

        navbar = soup.find("nav")
        a_tags = navbar.find_all("a")

        category_urls = [a["href"] for a in a_tags if category_str in a["href"]]
        category_urls = [url for url in category_urls if any(category in url for category in target_categories)]
        category_urls = self.format_urls_to_absolute_urls(category_urls)

        return category_urls

    def fetch_links_in_category(self, url):
        news_card_identifier = self.news_card_identifier

        with requests.get(url) as r:
            soup = BeautifulSoup(r.content, "lxml")
            if self.is_debug:
                print("status code :", r.status_code)

        content = asyncio.get_event_loop().run_until_complete(self.scroll_and_scrape(url, num_scroll=self.num_scroll))
        soup = BeautifulSoup(content, "lxml")

        cards = soup.select(news_card_identifier)
        news_urls = [card.find("a").attrs["href"] for card in cards if card.find("a")]
        news_urls = self.format_urls_to_absolute_urls(news_urls)

        return news_urls

    def fetch_content_in_news(self, url):
        content_identifier_dict = self.content_identifier_dict
        headline_identifier = content_identifier_dict["headline"]
        datetime_identifier = content_identifier_dict["datetime"]
        content_identifier = content_identifier_dict["content"]

        with requests.get(url) as r:
            soup = BeautifulSoup(r.content, "lxml")
            if self.is_debug:
                print("Status code :", r.status_code, "| url :", url)

        data_dict = {
            "headline": soup.select_one(headline_identifier).text.strip(),
            "language": self.language,
            "datetime": soup.select_one(datetime_identifier)["datetime"].strip(),
            "url": url,
            "content": soup.select_one(content_identifier).text.strip().replace("\n", " ")
        }

        return data_dict

    async def scroll_and_scrape(self, url, num_scroll=3):
        browser = await launch()
        page = await browser.newPage()
        await page.goto(url)

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
        return [url if url.startswith("http") else base_url + url for url in urls]

    def start_scraping(self):
        print("Fetching navbar ...", self.base_url)
        category_urls = self.fetch_navbar()
        print("Category URLs :", category_urls)

        data_dict_list = []
        for category_url in category_urls:
            print("Fetching all news links ...", category_url)
            news_urls = self.fetch_links_in_category(category_url)
            print("Total news links :", len(news_urls))

            print("Fetching each news content ...")
            for news_url in news_urls:
                try:
                    data_dict_list.append(self.fetch_content_in_news(news_url))
                except:
                    print("Error fetching :", news_url)

        return data_dict_list


def main():
    content_identifier_dict = {
        "headline": "h1.entry-title",
        "datetime": "time.entry-date",
        "content": "div.entry-content"
    }

    config = {
        "base_url": "https://portal.sina.com.hk/",
        "language": "zh",
        "category_str": "/category/",
        "target_categories": ["news-hongkong", "news-china"],#, "news-intl", "technology", "lifestyle"],
        "news_card_identifier": "article",
        "content_identifier_dict": content_identifier_dict,
        "is_debug": True
    }

    webscraper = WebScraper(config)
    data_dict_list = webscraper.start_scraping()
    df = pd.DataFrame(data_dict_list)
    df.to_csv("data/news_data.csv", sep="\t", index=False, encoding="utf-8")


if __name__ == '__main__':
    main()


