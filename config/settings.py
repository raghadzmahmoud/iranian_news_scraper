"""
إعدادات التطبيق الرئيسية
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database
DB_NAME = os.getenv("DB_NAME", "iran_news_pipeline")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_PORT = int(os.getenv("DB_PORT", 5432))

# Scraper
MAX_ITEMS_PER_SOURCE = int(os.getenv("MAX_ITEMS_PER_SOURCE", 5))
FETCH_FULL_ARTICLE = os.getenv("FETCH_FULL_ARTICLE", "true").lower() == "true"
DELAY_BETWEEN_REQUESTS = float(os.getenv("DELAY_BETWEEN_REQUESTS", 1.5))
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "news_output.json")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# RSS Feeds Configuration
FEEDS = {
    "ynet": {
        "name": "Ynet",
        "rss": "https://www.ynet.co.il/Integration/StoryRss2.xml",
        "article_selector": [
            "div.article-body",
            "div[class*='article_body']",
            "div[data-testid='article-body']",
            "div.text-editor-paragraph",
        ],
        "remove_selectors": [
            "div.taboola", "div[class*='taboola']",
            "div[class*='advertisement']", "div[class*='promo']",
            "div.related-articles", "aside", "footer",
            "div[class*='share']", "div[class*='social']",
            "script", "style", "nav",
        ]
    },
    "walla": {
        "name": "Walla",
        "rss": "https://rss.walla.co.il/feed/1",
        "article_selector": [
            "div.article-body",
            "div[class*='ArticleBody']",
            "div[class*='article-content']",
            "article div[class*='body']",
        ],
        "remove_selectors": [
            "div[class*='advertisement']", "div[class*='taboola']",
            "aside", "div[class*='related']", "div[class*='share']",
            "script", "style", "nav",
        ]
    },
    "maariv": {
        "name": "Maariv",
        "rss": "https://www.maariv.co.il/Rss/RssChadashot",
        "article_selector": [
            "div.article-body",
            "div[class*='article-body']",
            "div[itemprop='articleBody']",
            "div.content-body",
        ],
        "remove_selectors": [
            "div[class*='advertisement']", "div[class*='taboola']",
            "aside", "div[class*='related']",
            "script", "style", "nav",
        ]
    },
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "he-IL,he;q=0.9,en;q=0.8",
}
