"""
البرنامج الرئيسي - سحب البوستات من Telegram وتخزينها في قاعدة البيانات
"""
import re
from datetime import datetime
from config.settings import MAX_ITEMS_PER_SOURCE
from config.keywords import is_relevant_article, get_matching_keywords, debug_filter
from database.connection import db
from scrapers.telegram_scraper import telegram_scraper
from utils.logger import logger


def extract_channel_name(telegram_url: str) -> str:
    """
    استخراج اسم القناة من رابط Telegram
    
    مثال: https://t.me/s/idf_telegram → idf_telegram
    """
    match = re.search(r"t\.me/s/([a-zA-Z0-9_]+)", telegram_url)
    return match.group(1) if match else None


def scrape_telegram_sources(max_posts: int = 30) -> list:
    """
    سحب البوستات من جميع مصادر Telegram في قاعدة البيانات
    
    Args:
        max_posts: عدد البوستات لكل قناة
        
    Returns:
        قائمة البوستات المسحوبة
    """
    sources = db.get_telegram_sources()
    
    if not sources:
        logger.warning("⚠️  لا توجد مصادر Telegram في قاعدة البيانات")
        return []

    all_posts = []

    for source in sources:
        source_id = source['id']
        source_url = source['url']
        
        # استخراج اسم القناة من الرابط
        channel_name = extract_channel_name(source_url)
        
        if not channel_name:
            logger.warning(f"⚠️  لم يتمكن من استخراج اسم القناة من: {source_url}")
            continue

        # سحب البوستات
        posts = telegram_scraper.scrape_channel(channel_name, max_posts=max_posts)
        
        if not posts:
            logger.info(f"ℹ️  لا توجد بوستات جديدة من {channel_name}")
            continue

        # إضافة معرف المصدر لكل بوست
        for post in posts:
            post['source_id'] = source_id
            post['source_type_id'] = 3  # Telegram

        all_posts.extend(posts)

    return all_posts


def save_telegram_posts_to_db(posts: list, filter_enabled: bool = True):
    """
    حفظ بوستات Telegram في قاعدة البيانات
    فقط البوستات المتعلقة بإيران والتصعيد العسكري
    
    Args:
        posts: قائمة البوستات
        filter_enabled: تفعيل الفلترة
    """
    if not posts:
        logger.info("ℹ️  لا توجد بوستات للحفظ")
        return

    saved_count = 0
    skipped_count = 0
    filtered_count = 0

    for post in posts:
        # التحقق من وجود البوست بالفعل
        if db.url_exists(post['url']):
            logger.info(f"⏭️  تخطي (موجود): {post['url']}")
            skipped_count += 1
            continue

        # تطبيق الفلترة - جرب جميع اللغات
        if filter_enabled:
            content = post.get('content', '')
            channel = post.get('channel', '')
            
            is_relevant = False
            matched_keywords = []
            detected_language = None
            
            # جرب كل اللغات
            for lang in ["he", "ar", "en"]:
                is_relevant = is_relevant_article(channel, content, language=lang)
                if is_relevant:
                    matched_keywords = get_matching_keywords(channel, content, language=lang)
                    detected_language = lang
                    break
            
            if not is_relevant:
                # طباعة debug info للأخبار المرفوضة
                debug_info = debug_filter(channel, content, language=detected_language or "he")
                logger.info(f"🚫 فلترة (غير ذات صلة): {post['url'][:50]}...")
                logger.info(f"   Debug: {debug_info}")
                filtered_count += 1
                continue
            
            lang_name = {"he": "עברית", "ar": "عربي", "en": "English"}.get(detected_language, "unknown")
            logger.info(f"✅ مطابقة [{lang_name}]: {post['channel']} ({len(matched_keywords)} كلمات)")

        # تحضير بيانات المقالة
        article_data = {
            "url": post['url'],
            "full_text": post.get('content', ''),
            "pub_date": post.get('published_at'),
            "fetched_at": datetime.now().isoformat(),
            "image_url": post.get('media_url'),
            "tags": []
        }

        # إدراج في قاعدة البيانات
        result = db.insert_raw_data(post['source_id'], article_data)
        
        if result:
            saved_count += 1
            logger.info(f"✅ تم حفظ البوست: {post['url'][:50]}...")
        else:
            skipped_count += 1

    logger.info(f"\n📊 النتائج:")
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
    logger.info("🚀 بدء سحب بوستات Telegram الجديدة...")

    # الاتصال بقاعدة البيانات
    if not db.connect():
        logger.error("❌ فشل الاتصال بقاعدة البيانات")
        return

    # سحب البوستات
    posts = scrape_telegram_sources(max_posts=MAX_ITEMS_PER_SOURCE)

    if not posts:
        logger.info("ℹ️  لا توجد بوستات جديدة")
        db.close()
        return

    # حفظ في قاعدة البيانات مع الفلترة
    save_telegram_posts_to_db(posts, filter_enabled=True)

    # طباعة عينات
    seen_channels = set()
    for post in posts:
        if post['channel'] not in seen_channels:
            print_post_sample(post)
            seen_channels.add(post['channel'])

    logger.info(f"✅ انتهى! تم معالجة {len(posts)} بوست")

    # إغلاق الاتصال
    db.close()


if __name__ == "__main__":
    main()
