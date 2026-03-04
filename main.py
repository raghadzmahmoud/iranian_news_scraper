"""
البرنامج الرئيسي - سحب الأخبار من RSS و Telegram بالتوازي
"""
import re
import time
import threading
from datetime import datetime
from config.settings import (
    MAX_ITEMS_PER_SOURCE,
    FETCH_FULL_ARTICLE,
    DELAY_BETWEEN_REQUESTS
)
from config.keywords import is_relevant_article, get_matching_keywords, debug_filter
from database.connection import db
from scrapers.rss_scraper import parse_rss, load_rss_sources
from scrapers.article_scraper import scrape_full_article
from scrapers.telegram_scraper import telegram_scraper
from storage.database_storage import save_raw_data_to_db
from utils.logger import logger


def scrape_all_news(sources: list[str] = None, db_connection=None) -> list:
    """
    سحب الأخبار من جميع المصادر
    فقط الأخبار الجديدة (اللي ما موجودة بالـ URL)
    
    Args:
        sources: قائمة المصادر (None = الكل)
        db_connection: database connection (اختياري)
    
    Returns:
        قائمة المقالات الجديدة فقط
    """
    # استخدام الـ connection المعطاة أو الـ global db
    db_obj = db_connection if db_connection is not None else db
    
    # تحميل المصادر من JSON
    all_sources = load_rss_sources()
    
    if sources is None:
        sources = [s for s in all_sources.keys() if all_sources[s].get("enabled", True)]

    all_articles = []

    for source_key in sources:
        if source_key not in all_sources:
            logger.warning(f"⚠️  مصدر غير معروف: {source_key}")
            continue
        
        source = all_sources[source_key]
        if not source.get("enabled", True):
            logger.info(f"⏭️  تخطي المصدر المعطل: {source['name']}")
            continue

        # قراءة RSS
        articles = parse_rss(source_key, max_items=MAX_ITEMS_PER_SOURCE)
        
        # تصفية الأخبار الموجودة بالفعل
        new_articles = []
        for article in articles:
            if not db_obj.url_exists(article.url):
                new_articles.append(article)
            else:
                logger.info(f"⏭️  تخطي (موجودة): {article.title[:40]}...")
        
        if not new_articles:
            logger.info(f"ℹ️  لا توجد أخبار جديدة من {source['name']}")
            continue

        # سحب المقال الكامل فقط للأخبار الجديدة
        if FETCH_FULL_ARTICLE:
            logger.info(f"🔍 جاري سحب {len(new_articles)} مقال جديد...")
            import time
            for i, article in enumerate(new_articles):
                new_articles[i] = scrape_full_article(article, source_key)
                time.sleep(DELAY_BETWEEN_REQUESTS)

        all_articles.extend(new_articles)

    return all_articles


def print_article_sample(article):
    """طباعة عينة من المقالة"""
    print("\n" + "="*60)
    print(f"📰 {article.source}")
    print(f"📌 {article.title}")
    print(f"🕐 {article.pub_date}")
    print(f"🔗 {article.url}")
    if article.image_url:
        print(f"🖼️  {article.image_url}")
    if article.tags:
        print(f"🏷️  {', '.join(article.tags)}")
    print(f"\n📄 ملخص RSS:\n{article.summary[:200]}...")
    if article.full_text:
        print(f"\n📖 النص الكامل ({len(article.full_text)} حرف)")
    print("="*60)


def extract_channel_name(telegram_url: str) -> str:
    """استخراج اسم القناة من رابط Telegram"""
    match = re.search(r"t\.me/s/([a-zA-Z0-9_]+)", telegram_url)
    return match.group(1) if match else None


def scrape_telegram_sources(max_posts: int = 30, text_only: bool = True, db_connection=None) -> list:
    """سحب البوستات من جميع مصادر Telegram في قاعدة البيانات"""
    # استخدام الـ connection المعطاة أو الـ global db
    db_obj = db_connection if db_connection is not None else db
    
    sources = db_obj.get_telegram_sources()
    
    if not sources:
        logger.warning("⚠️  لا توجد مصادر Telegram في قاعدة البيانات")
        return []

    all_posts = []

    for source in sources:
        source_id = source['id']
        source_url = source['url']
        
        channel_name = extract_channel_name(source_url)
        
        if not channel_name:
            logger.warning(f"⚠️  لم يتمكن من استخراج اسم القناة من: {source_url}")
            continue

        posts = telegram_scraper.scrape_channel(channel_name, max_posts=max_posts, text_only=text_only)
        
        if not posts:
            logger.info(f"ℹ️  لا توجد بوستات جديدة من {channel_name}")
            continue

        for post in posts:
            post['source_id'] = source_id
            post['source_type_id'] = 3  # Telegram

        all_posts.extend(posts)

    return all_posts


def save_telegram_posts_to_db(posts: list, filter_enabled: bool = True, db_connection=None):
    """حفظ بوستات Telegram في قاعدة البيانات مع الفلترة"""
    # استخدام الـ connection المعطاة أو الـ global db
    db_obj = db_connection if db_connection is not None else db
    
    if not posts:
        logger.info("ℹ️  لا توجد بوستات للحفظ")
        return

    saved_count = 0
    skipped_count = 0
    filtered_count = 0

    for post in posts:
        if db_obj.url_exists(post['url']):
            logger.info(f"⏭️  تخطي (موجود): {post['url']}")
            skipped_count += 1
            continue

        if filter_enabled:
            content = post.get('content', '')
            channel = post.get('channel', '')
            
            is_relevant = False
            matched_keywords = []
            detected_language = None
            
            for lang in ["he", "ar", "en"]:
                is_relevant = is_relevant_article(channel, content, language=lang)
                if is_relevant:
                    matched_keywords = get_matching_keywords(channel, content, language=lang)
                    detected_language = lang
                    break
            
            if not is_relevant:
                debug_info = debug_filter(channel, content, language="he")
                logger.info(f"🚫 فلترة (غير ذات صلة): {post['url'][:50]}...")
                logger.info(f"   Debug: {debug_info}")
                filtered_count += 1
                continue
            
            lang_name = {"he": "עברית", "ar": "عربي", "en": "English"}.get(detected_language, "unknown")
            logger.info(f"✅ مطابقة [{lang_name}]: {post['channel']} ({len(matched_keywords)} كلمات)")

        article_data = {
            "url": post['url'],
            "full_text": post.get('content', ''),
            "pub_date": post.get('published_at'),
            "fetched_at": datetime.now().isoformat(),
            "image_url": post.get('media_url'),
            "tags": []
        }

        result = db_obj.insert_raw_data(post['source_id'], article_data)
        
        if result:
            saved_count += 1
            logger.info(f"✅ تم حفظ البوست: {post['url'][:50]}...")
        else:
            skipped_count += 1

    logger.info(f"\n📊 نتائج Telegram:")
    logger.info(f"  ✅ تم حفظ: {saved_count} بوست")
    logger.info(f"  ⏭️  تم تخطي: {skipped_count} موجود")
    logger.info(f"  🚫 تم فلترة: {filtered_count} غير ذات صلة")


def print_post_sample(post: dict):
    """طباعة عينة من البوست"""
    print("\n" + "="*60)
    print(f"📨 {post['channel']}")
    print(f"🔗 {post['url']}")
    print(f"🕐 {post.get('published_at', 'غير محدد')}")
    
    if post.get('media_type'):
        media_labels = {
            "image": "🖼️ ",
            "video": "🎥",
            "video_thumb": "🎞️",
            "document": "📎"
        }
        label = media_labels.get(post['media_type'], "📁")
        print(f"{label}  [{post['media_type']}]  {post.get('media_url', '')[:70]}")
        if post.get('media_local'):
            print(f"    💾 محفوظ: {post['media_local']}")
    
    print(f"\n📝 النص:\n{post.get('content', '(بدون نص)')[:300]}")
    print("="*60)


def main():
    """الدالة الرئيسية"""
    logger.info("🚀 بدء سحب الأخبار والبوستات الجديدة (بالتوازي)...")

    # الاتصال بقاعدة البيانات
    if not db.connect():
        logger.error("❌ فشل الاتصال بقاعدة البيانات")
        return

    # ============================================================
    # Worker 1: سحب أخبار RSS
    # ============================================================
    def worker_rss():
        """Worker لسحب أخبار RSS"""
        logger.info("\n" + "="*60)
        logger.info("📰 [Worker 1] بدء سحب أخبار RSS...")
        logger.info("="*60)

        SOURCE_ID_MAP = {
            "ynet": 1,
            "walla": 2,
            "maariv": 3,
        }

        articles = scrape_all_news(sources=["ynet", "walla", "maariv"])

        if articles:
            for source_key, source_id in SOURCE_ID_MAP.items():
                source_articles = [a for a in articles if a.source == FEEDS[source_key]["name"]]
                if source_articles:
                    save_raw_data_to_db(source_articles, source_id, filter_enabled=True)

            seen_sources = set()
            for article in articles:
                if article.source not in seen_sources:
                    print_article_sample(article)
                    seen_sources.add(article.source)

            logger.info(f"✅ [Worker 1] انتهى RSS! تم حفظ {len(articles)} مقال جديد")
        else:
            logger.info("ℹ️  [Worker 1] لا توجد أخبار جديدة من RSS")

    # ============================================================
    # Worker 2: سحب بوستات Telegram
    # ============================================================
    def worker_telegram():
        """Worker لسحب بوستات Telegram"""
        logger.info("\n" + "="*60)
        logger.info("📨 [Worker 2] بدء سحب بوستات Telegram...")
        logger.info("="*60)

        posts = scrape_telegram_sources(max_posts=MAX_ITEMS_PER_SOURCE)

        if posts:
            save_telegram_posts_to_db(posts, filter_enabled=True)

            seen_channels = set()
            for post in posts:
                if post['channel'] not in seen_channels:
                    print_post_sample(post)
                    seen_channels.add(post['channel'])

            logger.info(f"✅ [Worker 2] انتهى Telegram! تم معالجة {len(posts)} بوست")
        else:
            logger.info("ℹ️  [Worker 2] لا توجد بوستات جديدة من Telegram")

    # ============================================================
    # تشغيل الـ Workers بالتوازي
    # ============================================================
    thread_rss = threading.Thread(target=worker_rss, name="RSS-Worker", daemon=False)
    thread_telegram = threading.Thread(target=worker_telegram, name="Telegram-Worker", daemon=False)

    logger.info("\n" + "="*60)
    logger.info("🔄 تشغيل Worker 1 (RSS) و Worker 2 (Telegram) بالتوازي...")
    logger.info("="*60)

    # بدء الـ Threads
    thread_rss.start()
    thread_telegram.start()

    # انتظار انتهاء الاثنين
    thread_rss.join()
    thread_telegram.join()

    # ============================================================
    # الخلاصة
    # ============================================================
    logger.info("\n" + "="*60)
    logger.info("✅ انتهى! تم سحب RSS و Telegram بنجاح (بالتوازي)")
    logger.info("="*60)

    db.close()


if __name__ == "__main__":
    main()
