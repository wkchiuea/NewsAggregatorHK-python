from requests_html import HTMLSession, HTML
from pyppeteer import launch
import asyncio


def fetch_navbar(url, section_str):
    print("Fetching navbar ...")

    session = HTMLSession()
    r = session.get(url)
    print("Status code :", r.status_code)
    print(r.html)

    navbar = r.html.find("nav", first=True)
    a_tags = navbar.find("a")

    section_urls = [a.base_url + a.attrs.get("href") for a in a_tags if section_str in a.attrs.get("href")]
    print("Section URLs :", section_urls)

    session.close()

    return section_urls


async def scroll_and_scrape(url, num_scroll=4):
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


def fetch_links_in_section(base_url, url):
    print("Fetching all news links ...")

    session = HTMLSession()
    r = session.get(url)
    print("status code :", r.status_code)
    print(r.html)

    content = asyncio.get_event_loop().run_until_complete(scroll_and_scrape(url, num_scroll=1))
    body = HTML(html=content)

    cards = body.find(".content-card")
    print("Cards length :", len(cards))
    news_urls = [base_url + card.find("a", first=True).attrs["href"] for card in cards if card.find("a")]

    for link in news_urls:
        print(link)

    session.close()

    return news_urls


def fetch_content_in_news(url="https://www.hk01.com/%E7%A4%BE%E6%9C%83%E6%96%B0%E8%81%9E/1005551/%E8%91%B5%E8%8A%B3%E7%89%9B%E8%A7%92%E4%B8%80%E5%BC%B5%E5%96%AE4-7%E8%90%AC-%E8%80%81%E9%97%86%E9%BB%83%E5%82%91%E9%BE%8D-%E6%B6%88%E8%B2%BB%E5%AF%92%E5%86%AC%E4%B8%AD-%E7%B0%A1%E7%9B%B4%E4%BF%82%E5%86%8D%E7%94%9F%E7%88%B6%E6%AF%8D"):
    print("Fetching each news content ...")

    session = HTMLSession()
    r = session.get(url)
    print("status code :", r.status_code)
    print(r.html)

    data_dict = {
        "date": r.html.find("div[data-testid='article-publish-info']", first=True).text,
        "headline": r.html.find("#articleTitle").text,
        "url": url,
        "opening_text": r.html.find("article#article-content-section", first=True).find("p", first=True).text
    }

    session.close()

    return data_dict


def main():
    base_url = "https://www.hk01.com"
    section_str = "/channel/"
    section_urls = fetch_navbar(base_url, section_str)

    for url in section_urls:
        news_urls = fetch_links_in_section(base_url, url)

        for news_url in news_urls:
            data_dict = fetch_content_in_news(news_url)


if __name__ == '__main__':
    # main()
    fetch_content_in_news()