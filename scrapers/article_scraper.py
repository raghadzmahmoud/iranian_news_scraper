"""
سحب المقالات الكاملة
"""
import re
import requests
from bs4 import BeautifulSoup
from models.article import NewsArticle
from config.settings import FEEDS, HEADERS
from utils.logger import logger


def scrape_full_article(article: NewsArticle, source_key: str) -> NewsArticle:
    """
    سحب النص الكامل للمقالة من الموقع + الصور
    
    Args:
        article: كائن NewsArticle
        source_key: مفتاح المصدر
    
    Returns:
        NewsArticle محدثة بالنص الكامل والصور
    """
    if source_key not in FEEDS:
        logger.error(f"❌ مصدر غير معروف: {source_key}")
        return article

    config = FEEDS[source_key]

    try:
        resp = requests.get(article.url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        resp.encoding = "utf-8"

        soup = BeautifulSoup(resp.text, "lxml")

        # إزالة العناصر غير المرغوبة
        for selector in config["remove_selectors"]:
            for el in soup.select(selector):
                el.decompose()

        # إزالة سكريبتات و ستايلات
        for tag in soup(["script", "style", "noscript", "iframe", "ins"]):
            tag.decompose()

        # البحث عن محتوى المقال
        article_body = None
        for selector in config["article_selector"]:
            article_body = soup.select_one(selector)
            if article_body:
                break

        if not article_body:
            article_body = soup.find("article")

        if not article_body:
            divs = soup.find_all("div")
            article_body = max(
                divs,
                key=lambda d: len(d.get_text(strip=True)),
                default=None
            )

        if not article_body:
            logger.warning(f"⚠️  لم يُعثر على محتوى: {article.url}")
            return article

        # استخراج الصور من المقالة إذا لم تكن موجودة
        if not article.image_url:
            img_tag = article_body.find("img")
            if img_tag:
                img_src = img_tag.get("src") or img_tag.get("data-src")
                if img_src:
                    # تحويل الروابط النسبية إلى مطلقة
                    if img_src.startswith("http"):
                        article.image_url = img_src
                    else:
                        from urllib.parse import urljoin
                        article.image_url = urljoin(article.url, img_src)

        # استخراج الفقرات
        paragraphs = []
        for p in article_body.find_all("p"):
            text = p.get_text(separator=" ", strip=True)
            if text and len(text) > 30:
                paragraphs.append(text)

        if len(paragraphs) < 2:
            full_text = article_body.get_text(separator="\n", strip=True)
            full_text = re.sub(r'\n{3,}', '\n\n', full_text)
            article.full_text = full_text
        else:
            article.paragraphs = paragraphs
            article.full_text = "\n\n".join(paragraphs)

        logger.info(f"📰 {article.title[:50]}... ({len(article.full_text)} حرف)")
        if article.image_url:
            logger.info(f"🖼️  صورة: {article.image_url[:60]}...")

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ خطأ في الاتصال: {e}")
    except Exception as e:
        logger.error(f"❌ خطأ غير متوقع: {e}")

    return article
