# Feed configuration for the news_rss connector

NEWS_FEEDS = {
    {
        "source_id": "npr_world",
        "feed_url": "https://feeds.npr.org/1004/rss.xml",
    },
    {
        "source_id": "defense_news",
        "feed_url": "https://www.defensenews.com/arc/outboundfeeds/rss/?outputType=xml",
    },
}
CONGRESS_CONFIG = {
    "source_id": "congress_gov",
    "base_url": "https://api.congress.gov/v3",
    "congress": 119,
    "sort": "updateDate+desc",
    "max_bills": 100,
    "page_size": 20,
}