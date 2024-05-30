from apify_client import ApifyClient
import pandas as pd
import re
import os
import argparse
import urllib.request
from urllib.parse import urlparse, urlunparse
from pymongo import MongoClient


mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client['raw_news']
news_data_collection = db['news_data']
comments_collection = db['comments']
job_log_collection = db['job_log']


def get_api_client():
    APIFY_API_KEY = os.getenv('APIFY_API_TOKEN')
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


def get_comments(client, results_limit=25, comments_limit=50):
    fb_posts_scraper_id, fb_comments_scraper_id = get_actors(client)

    # Get last 25 posts from HK01
    input_get_post = {
        "startUrls": [{ "url": "https://www.facebook.com/hk01wemedia/" }],
        "resultsLimit": results_limit,
    }
    # Run the Actor and wait for it to finish
    run_get_post = client.actor(fb_posts_scraper_id).call(run_input=input_get_post)

    # Fetch and print Actor results from the run's dataset (if there are any)
    output_urls = []
    for item in client.dataset(run_get_post["defaultDatasetId"]).iterate_items():
        if "01新聞" in item.get("text", ""):
            output_urls.append({"url": item["url"]})


    # Prepare the Actor input
    input_get_comments = {
        "startUrls": output_urls,
        "resultsLimit": comments_limit,
        "includeNestedComments": False,
        "viewOption": "RANKED_UNFILTERED",
    }
    # Run the Actor and wait for it to finish
    run_get_comments = client.actor(fb_comments_scraper_id).call(run_input=input_get_comments)

    # Fetch Actor results from the run's dataset and create a DataFrame
    items = list(client.dataset(run_get_comments["defaultDatasetId"]).iterate_items())
    df = pd.DataFrame(items)

    return df


def extract_and_expand_bityl_link(post_title):
    match = re.search(r"全文：(.*?)\n", post_title)
    if match:
        bityl_link = match.group(1)
        try:
            with urllib.request.urlopen(bityl_link) as response:
                parsed_url = urlparse(response.geturl())
                clean_url = urlunparse(parsed_url._replace(query=""))
                return clean_url
        except:
            return None
    else:
        return None


def get_urls_from_db(platform='hk01'):
    print("Start getting urls from news_data collection...")
    try:
        existing_urls = news_data_collection.find(
            {"platform": platform},
            {"url": 1, "_id": 0}  # Only fetch the 'url' field
        )
        return {doc['url'] for doc in existing_urls}
    except Exception as e:
        return set()


def get_comments_from_db(platform='hk01'):
    print("Start getting urls from comments collection...")
    try:
        existing_comments = comments_collection.find(
            {"platform": platform},
            {"commentId": 1, "targetUrl": 1, "_id": 0}
        )
        return {(doc['targetUrl'], doc['commentId']) for doc in existing_comments}
    except Exception as e:
        return set()


def insert_comments_to_db(comments):
    print("Start inserting to comments collection...")
    try:
        result = comments_collection.insert_many(comments)
        print(f"Inserted IDs: {result.inserted_ids}")
    except Exception as e:
        print(e)


def main(args):
    results_limit = args.results_limit if args is not None else 25
    comments_limit = args.comments_limit if args is not None else 50
    print("Starting Facebook comments scraping...")
    print(f"Posts Limit : {results_limit} \n Comments Limit : {comments_limit}")

    client = get_api_client()
    df = get_comments(client, results_limit, comments_limit)

    # Add a new column with expanded news urls and filter targetUrl to preserve only those in news_data
    df["targetUrl"] = df["postTitle"].apply(extract_and_expand_bityl_link)
    existing_urls = get_urls_from_db(platform="hk01")
    df = df[df["targetUrl"].isin(existing_urls)]

    # with targetUrl, only get those comments not in db
    df["commentId"] = df["commentUrl"].apply(lambda url: url.split('?')[1].split('=')[1])
    existing_comments = get_comments_from_db(platform="hk01")
    df = df[~df.apply(lambda row: (row["targetUrl"], row["commentId"]) in existing_comments, axis=1)]

    # Create a new df with certain columns
    df = df[['date', 'text', 'postTitle', 'targetUrl', 'commentId']]
    df['platform'] = 'hk01'

    # Transform the df to a list of dicts
    results = df.to_dict(orient='records')
    insert_comments_to_db(results)

    print("Comments Scraping Completed!!!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Limit the scraping results")
    parser.add_argument('results_limit', type=int, nargs='?', default=25,
                        help='Scraping results limit (default: 25)')
    parser.add_argument('--comments_limit', type=int, nargs='?', default=50,
                        help='Limit the number of comment')
    args = parser.parse_args()

    main(args)

# python fb_comment.py 25 --comments_limit 50


