import requests
import pandas as pd
from datetime import datetime

# Base URL of your API
BASE_IP = ''
BASE_URL = f'http://{BASE_IP}:5000'

def query_news(before_datetime=None, after_datetime=None, start_datetime=None, end_datetime=None, platform=None):
    """
    Query the NewsResource endpoint with the given parameters.
    """
    print("Querying NewsResource for ...")
    print("before_datetime:", before_datetime)
    print("after_datetime:", after_datetime)
    print("start_datetime:", start_datetime)
    print("end_datetime:", end_datetime)
    print("platform:", platform)
    params = {}
    if before_datetime:
        params['before_datetime'] = before_datetime.strftime("%Y-%m-%d %H:%M")
    if after_datetime:
        params['after_datetime'] = after_datetime.strftime("%Y-%m-%d %H:%M")
    if start_datetime and end_datetime:
        params['start_datetime'] = start_datetime.strftime("%Y-%m-%d %H:%M")
        params['end_datetime'] = end_datetime.strftime("%Y-%m-%d %H:%M")
    if platform:
        params['platform'] = platform

    response = requests.get(f"{BASE_URL}/news", params=params)
    return response.json()

def query_comments(target_urls=None, platform=None):
    """
    Query the CommentsResource endpoint with the given parameters.
    """
    params = {}
    if target_urls:
        params['targetUrl'] = target_urls
    if platform:
        params['platform'] = platform

    response = requests.get(f"{BASE_URL}/comments", params=params)
    return response.json()

# Example usage
if __name__ == "__main__":
    # Query NewsResource
    after_datetime = datetime(2024, 5, 31, 11, 0)
    platform = 'now'
    news_data = query_news(after_datetime=after_datetime, platform=platform)
    news_data = pd.DataFrame(news_data)
    print(news_data)
    # print(len(news_data), "News Data:", news_data[0])

    # Query CommentsResource
    # target_urls = ['http://example.com/article1', 'http://example.com/article2']
    # platform = 'Twitter'
    # comments_data = query_comments(target_urls=target_urls, platform=platform)
    # print("Comments Data:", comments_data)
