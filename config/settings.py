"""
إعدادات التطبيق الرئيسية
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================
# Database Configuration with UTF-8 Support
# ============================================
DB_NAME = os.getenv("DB_NAME", "iran_news_pipeline")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_CONFIG = {
    'dbname': DB_NAME,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'host': DB_HOST,
    'port': DB_PORT,
    'options': '-c client_encoding=utf8 -c standard_conforming_strings=on',
    'client_encoding': 'utf8'
}

# ============================================
# AI Models Configuration
# ============================================
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
GEMINI_IMAGE_MODEL = os.getenv('GEMINI_IMAGE_MODEL', 'gemini-2.5-flash-image')

# ============================================
# AWS S3 Configuration
# ============================================
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_DEFAULT_REGION', os.getenv('AWS_REGION', 'us-east-1'))
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

# S3 Folder Structure - Original Content
S3_ORIGINAL_IMAGES_FOLDER = os.getenv('S3_ORIGINAL_IMAGES_FOLDER', 'original/images/')
S3_ORIGINAL_VIDEOS_FOLDER = os.getenv('S3_ORIGINAL_VIDEOS_FOLDER', 'original/videos/')
S3_ORIGINAL_AUDIOS_FOLDER = os.getenv('S3_ORIGINAL_AUDIOS_FOLDER', 'original/audios/')

# S3 Folder Structure - AI Generated Content
S3_GENERATED_IMAGES_FOLDER = os.getenv('S3_GENERATED_IMAGES_FOLDER', 'generated/images/')
S3_GENERATED_AUDIOS_FOLDER = os.getenv('S3_GENERATED_AUDIOS_FOLDER', 'generated/audios/')
S3_GENERATED_VIDEOS_FOLDER = os.getenv('S3_GENERATED_VIDEOS_FOLDER', 'generated/videos/')

# ============================================
# Audio Input Settings
# ============================================
MAX_AUDIO_SIZE_MB = int(os.getenv('MAX_AUDIO_SIZE_MB', 50))
ALLOWED_AUDIO_FORMATS = os.getenv('ALLOWED_AUDIO_FORMATS', 'mp3,wav,ogg,m4a,webm').split(',')

# ============================================
# Video Input Settings
# ============================================
MAX_VIDEO_SIZE_MB = int(os.getenv('MAX_VIDEO_SIZE_MB', 500))
ALLOWED_VIDEO_FORMATS = os.getenv('ALLOWED_VIDEO_FORMATS', 'mp4,avi,mov,mkv,webm').split(',')

# ============================================
# Scraper Configuration
# ============================================
MAX_ITEMS_PER_SOURCE = int(os.getenv("MAX_ITEMS_PER_SOURCE", 5))
FETCH_FULL_ARTICLE = os.getenv("FETCH_FULL_ARTICLE", "true").lower() == "true"
DELAY_BETWEEN_REQUESTS = float(os.getenv("DELAY_BETWEEN_REQUESTS", 1.5))
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "news_output.json")

# ============================================
# Logging Configuration
# ============================================
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
