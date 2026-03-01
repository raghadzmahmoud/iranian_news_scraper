"""
قارئ RSS
"""
import feedparser
from bs4 import BeautifulSoup
from models.article import NewsArticle
from config.settings import FEEDS
from utils.logger import logger


def parse_rss(source_key: str, max_items: int = 10) -> list[NewsArticle]:
    """
    قراءة RSS وإرجاع قائمة مقالات
    
    Args:
        source_key: مفتاح المصدر (ynet, walla, maariv)
        max_items: عدد المقالات المطلوبة
    
    Returns:
        قائمة NewsArticle
    """
    if source_key not in FEEDS:
        logger.error(f"❌ مصدر غير معروف: {source_key}")
        return []

    config = FEEDS[source_key]
    logger.info(f"📡 جاري قراءة RSS: {config['name']} ...")

    try:
        feed = feedparser.parse(config["rss"])
        articles = []

        for entry in feed.entries[:max_items]:
            # استخراج الصورة
            image_url = None
            if hasattr(entry, "media_content"):
                image_url = entry.media_content[0].get("url")
            elif hasattr(entry, "summary"):
                soup = BeautifulSoup(entry.get("summary", ""), "lxml")
                img = soup.find("img")
                if img:
                    image_url = img.get("src")

            # استخراج النص الخام من description
            raw_description = entry.get("summary", "")
            soup_desc = BeautifulSoup(raw_description, "lxml")
            clean_summary = soup_desc.get_text(separator=" ", strip=True)

            # Tags
            tags = []
            raw_tags = entry.get("tags", [])
            if isinstance(raw_tags, list):
                tags = [t.get("term", "") for t in raw_tags]
            elif isinstance(raw_tags, str):
                tags = [t.strip() for t in raw_tags.split(",")]

            article = NewsArticle(
                source=config["name"],
                title=entry.get("title", "").strip(),
                url=entry.get("link", "").strip(),
                pub_date=entry.get("published", ""),
                summary=clean_summary,
                image_url=image_url,
                tags=tags,
            )
            articles.append(article)

        logger.info(f"✅ تم جلب {len(articles)} مقال من RSS")
        return articles

    except Exception as e:
        logger.error(f"❌ خطأ في قراءة RSS: {e}")
        return []
