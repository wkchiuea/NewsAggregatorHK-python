import requests
from bs4 import BeautifulSoup
from pyppeteer import launch
import asyncio
import nest_asyncio
import pandas as pd


class WebScraper:

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }

    def __init__(self, config):
        self.base_url = config.get("base_url", "")
        self.language = config.get("language", "")
        self.navbar = config.get("navbar", "")
        self.category_str = config.get("category_str", "")
        self.target_categories = config.get("target_categories", "")

        self.num_scroll = config.get("num_scroll", 3)
        self.news_card_identifier = config.get("news_card_identifier", "")
        self.headline_identifier = config.get("headline_identifier", "")
        self.datetime_identifier = config.get("datetime_identifier", "")
        self.content_identifier = config.get("content_identifier", "")

        self.is_debug = config.get("is_debug", False)

    def fetch_navbar(self):
        base_url = self.base_url
        navbar = self.navbar
        category_str = self.category_str
        target_categories = self.target_categories

        with requests.get(base_url, headers=self.headers) as r:
            soup = BeautifulSoup(r.content, "lxml")
            if self.is_debug:
                print("Status code :", r.status_code)

        navlist = soup.select_one(navbar)
        a_tags = navlist.find_all("a")

        category_urls = [a["href"] for a in a_tags if category_str in a["href"]]
        category_urls = [url for url in category_urls if any(category in url for category in target_categories)]
        category_urls = self.format_urls_to_absolute_urls(category_urls)

        return category_urls

    def fetch_links_in_category(self, url):
        news_card_identifier = self.news_card_identifier

        with requests.get(url, headers=self.headers) as r:
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
        headline_identifier = self.headline_identifier
        datetime_identifier = self.datetime_identifier
        content_identifier = self.content_identifier

        with requests.get(url, headers=self.headers) as r:
            soup = BeautifulSoup(r.content, "lxml")
            if self.is_debug:
                print("Status code :", r.status_code, "| url :", url)

        data_dict = {
            "headline": soup.select_one(headline_identifier).text.strip(),
            "language": self.language,
            "datetime": soup.select_one(datetime_identifier).text.strip(),
            "url": url,
            "content": soup.select_one(content_identifier).text.strip().replace("\n", " ")
        }

        return data_dict

    async def scroll_and_scrape(self, url, num_scroll=3):
        browser = await launch()
        page = await browser.newPage()
        await page.setUserAgent(self.headers['User-Agent'])
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

    def test_scraping(self):
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
                    fetched_data = self.fetch_content_in_news(news_url)
                    for k, v in fetched_data.items():
                        print("************************************")
                        print(k)
                        print(v)
                        print('\n')
                    data_dict_list.append(fetched_data)
                except Exception as e:
                    print("Error fetching :", news_url)
                    print(e)
                break
            break

        return data_dict_list


def main():
    config = {
        "name": "sina",
        "base_url": "https://portal.sina.com.hk/",
        "language": "zh",
        "navbar": "nav",
        "category_str": "/category/",
        "target_categories": ['news-hongkong', 'news-china', 'news-intl', 'technology'],
        "news_card_identifier": "article",
        "headline_identifier": "h1.entry-title",
        "datetime_identifier": "time.entry-date",
        "content_identifier": "div.entry-content",
        "is_debug": True
    }

    webscraper = WebScraper(config)
    # data_dict_list = webscraper.start_scraping()
    data_dict_list = webscraper.test_scraping()
    df = pd.DataFrame(data_dict_list)
    df.to_csv(f"data/news_data_{config['name']}_{config['language']}.csv", sep="\t", index=False, encoding="utf-8")


if __name__ == '__main__':
    main()


