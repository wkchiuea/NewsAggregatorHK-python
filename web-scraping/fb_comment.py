from apify_client import ApifyClient
import logging
import re
import os
import argparse
from datetime import datetime
import urllib.request
from urllib.parse import urlparse, urlunparse
from pymongo import MongoClient


mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client['raw_news']
news_data_collection = db['news_data']
comments_collection = db['comments']
job_log_collection = db['job_log']


newsFB = {
    "hk01": "https://www.facebook.com/hk01.news",
    "hket": "https://www.facebook.com/hketpage",
    "am730": "https://www.facebook.com/am730hk",
    "hkej": "https://www.facebook.com/hongkongeconomicjournal",
    "tvb": "https://www.facebook.com/tvbnewsofficial",
    "singtao": "https://www.facebook.com/singtaohk",
    "std": "https://www.facebook.com/stheadlinehk",
    "sina": "https://www.facebook.com/hongkongsina",
    "hk01_2": "https://www.facebook.com/hk01wemedia/",
    "oncc": "https://www.facebook.com/onccnews/"
}


def get_logger(is_file=False, is_console=False):

    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Set the minimum log level

    # Create a formatter and set it for both handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')

    if is_file:
        # Create a file handler for output file
        file_handler = logging.FileHandler('fb_comment.log')
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


def get_api_client():
    APIFY_API_KEY = os.getenv('APIFY_API_KEY')
    if APIFY_API_KEY is None:
        raise ValueError('API_TOKEN environment variable not set')

    # Initialize the ApifyClient with your API token
    client = ApifyClient(APIFY_API_KEY)

    return client


def get_actors(client):
    actors_list = client.actors().list()
    fb_posts_scraper_id, fb_comments_scraper_id = "", ""
    for actor in actors_list.items:
        if actor['name'] == 'facebook-posts-scraper':
            fb_posts_scraper_id = actor['id']
        if actor['name'] == 'facebook-comments-scraper':
            fb_comments_scraper_id = actor['id']

    return fb_posts_scraper_id, fb_comments_scraper_id


def get_comments(client, homepage_url, results_limit=25, comments_limit=50):
    logger.info("Getting comments urls from facebook...")
    fb_posts_scraper_id, fb_comments_scraper_id = get_actors(client)

    # Get last 25 posts
    input_get_post = {
        "startUrls": [{"url": homepage_url}],
        "resultsLimit": results_limit,
    }
    # Run the Actor and wait for it to finish
    run_get_post = client.actor(fb_posts_scraper_id).call(run_input=input_get_post)

    # Fetch and print Actor results from the run's dataset (if there are any)
    output_urls = []
    for item in client.dataset(run_get_post["defaultDatasetId"]).iterate_items():
        output_urls.append({"url": item["url"]})

    logger.info("Getting comments...")
    # Prepare the Actor input
    input_get_comments = {
        "startUrls": output_urls,
        "resultsLimit": comments_limit,
        "includeNestedComments": False,
        "viewOption": "RANKED_UNFILTERED",
    }
    # Run the Actor and wait for it to finish
    run_get_comments = client.actor(fb_comments_scraper_id).call(run_input=input_get_comments)

    logger.info("Successfully fetch comments !!!")

    # Fetch Actor results from the run's dataset
    items = list(client.dataset(run_get_comments["defaultDatasetId"]).iterate_items())

    return items


def extract_first_url(text):
    if isinstance(text, str):
        match = re.search(r"https?://[^\s]+", text)
        if match:
            return match.group(0)
    return None


def extract_first_url_for_each_fb_url(items):
    # Create a dictionary to store the first URL for each facebookUrl
    facebook_url_dict = {}

    # Populate the dictionary from the text column
    for item in items:
        facebook_url = item.get("facebookUrl", "")
        url = extract_first_url(item.get("text", ""))
        if facebook_url and url and facebook_url not in facebook_url_dict:
            facebook_url_dict[facebook_url] = url

    # Extract URLs from the postTitle
    for item in items:
        item["postTitleURL"] = extract_first_url(item.get("postTitle", ""))

    # Prioritize the URL from postTitle if available, otherwise use the one from text
    for item in items:
        post_title_url = item.get("postTitleURL")
        facebook_url = item.get("facebookUrl", "")
        item["targetUrl"] = post_title_url if post_title_url else facebook_url_dict.get(facebook_url, None)

    # Remove items where the News Link is None
    items = [item for item in items if item.get("targetUrl")]

    # Remove specific keys from the dictionaries
    keys_to_remove = ["id", "feedbackId", "profileUrl", "profilePicture", "profileId", "profileName", "facebookId", "pageAdLibrary", "attachments"]

    for item in items:
        for key in keys_to_remove:
            if key in item:
                del item[key]

    return items


def expand_shortened_link(url):
    try:
        if "m.hkej.com" in url:
          url = url.replace("https://m.hkej.com/landing/mobarticle2/id/", "https://www2.hkej.com/instantnews/current/article/")
          return url
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        )
        with urllib.request.urlopen(req) as response:
            expanded_url = response.geturl()
            parsed_url = urlparse(expanded_url)
            clean_url = urlunparse(parsed_url._replace(query=""))
            return clean_url
    except Exception as e:
        return url


def get_urls_from_db(platform='hk01'):
    logger.info("Start getting urls from news_data collection...")
    try:
        existing_urls = news_data_collection.find(
            {"platform": platform},
            {"url": 1, "_id": 0}  # Only fetch the 'url' field
        )
        return {doc['url'] for doc in existing_urls}
    except Exception as e:
        return set()


def get_comments_from_db(platform='hk01'):
    logger.info("Start getting urls from comments collection...")
    try:
        existing_comments = comments_collection.find(
            {"platform": platform},
            {"commentId": 1, "targetUrl": 1, "_id": 0}
        )
        return {(doc['targetUrl'], doc['commentId']) for doc in existing_comments}
    except Exception as e:
        return set()


def insert_comments_to_db(comments):
    logger.info("Start inserting to comments collection...")
    try:
        result = comments_collection.insert_many(comments)
        logger.info(f"Inserted IDs: {result.inserted_ids}")
    except Exception as e:
        logger.info(e)


def main(args):
    results_limit = args.results_limit if args is not None else 25
    comments_limit = args.comments_limit if args is not None else 50
    logger.info("Starting Facebook comments scraping...")
    logger.info(f"Posts Limit : {results_limit} \n Comments Limit : {comments_limit}")

    client = get_api_client()
    for _platform, homepage_url in newsFB.items():
        platform = _platform if _platform != "hk01_2" else "hk01"
        logger.info("=======================================")
        logger.info(f"Starting fetching platform: {platform}")

        comments = get_comments(client, homepage_url, results_limit, comments_limit)
        comments = extract_first_url_for_each_fb_url(comments)

        # Define the domains to check for
        domains = ["bityl.co", "tinyurl.com", "buff.ly", "bit.ly", "m.hkej.com"]
        for item in comments:
            news_link = item.get("targetUrl", "")
            if any(domain in news_link for domain in domains):
                item["targetUrl"] = expand_shortened_link(news_link)

        existing_urls = get_urls_from_db(platform)
        comments = [c for c in comments if c["targetUrl"] in existing_urls]

        # With targetUrl, only get those comments not in db
        for comment in comments:
            try:
                comment["commentId"] = comment["commentUrl"].split('?')[1].split('=')[1]
            except:
                comment["commentId"] = 0
                continue

        existing_comments = get_comments_from_db(platform)
        comments = [c for c in comments if (c["targetUrl"], c["commentId"]) not in existing_comments]

        # Create a new list with certain fields
        results = []
        for c in comments:
            if 'text' not in c.keys():
                continue
            results.append({
                'date': c['date'],
                'text': c['text'],
                'postTitle': c['postTitle'],
                'targetUrl': c['targetUrl'],
                'commentId': c['commentId'],
                'platform': platform
            })

        insert_comments_to_db(results)
        del comments
        del existing_comments
        del results
        logger.info(f"Comments Scraping Complete for {platform} ~~~")

    logger.info("Comments Scraping Completed!!!")


logger = get_logger(is_file=False, is_console=True)


if __name__ == "__main__":
    t = datetime.now().strftime('%Y-%m-%d %H:%M')
    logger.info("***************************************************")
    logger.info(f"************** {t} *******************")
    logger.info("***************************************************")

    parser = argparse.ArgumentParser(description="Limit the scraping results")
    parser.add_argument('results_limit', type=int, nargs='?', default=25,
                        help='Scraping results limit (default: 25)')
    parser.add_argument('--comments_limit', type=int, nargs='?', default=50,
                        help='Limit the number of comment')
    args = parser.parse_args()

    main(args)