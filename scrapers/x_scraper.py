"""
X (Twitter) Scraper - سحب من قاعدة البيانات
يقرأ المصادر من الداتابيس (source_type_id = 7)
ويخزن في raw_news مع الفلترة ومنع التكرار
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional
from database.connection import db
from storage.article_processor import ArticleProcessor
from models.article import NewsArticle
from utils.logger import logger
from config.settings import (
    X_AUTH_TOKEN,
    X_CT0_TOKEN,
    X_MAX_TWEETS_PER_ACCOUNT,
    X_DELAY_BETWEEN_ACCOUNTS,
    X_DEBUG,
    X_COOKIES_FILE
)

# Fix encoding on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Playwright toggle
from config.settings import USE_X_PLAYWRIGHT
if USE_X_PLAYWRIGHT:
    from .x_playwright import scrape_all_playwright, NewsArticle
    HAS_PLAYWRIGHT = True
else:
    HAS_PLAYWRIGHT = False


# ============================================================
# ⚙️ الإعدادات من .env
# ============================================================

COOKIES_FILE = X_COOKIES_FILE
MAX_TWEETS_PER_ACCOUNT = X_MAX_TWEETS_PER_ACCOUNT
DELAY_BETWEEN_ACCOUNTS = X_DELAY_BETWEEN_ACCOUNTS
DEBUG = X_DEBUG

# ============================================================


def extract_username_from_url(url: str) -> Optional[str]:
    """استخراج اليوزرنيم من رابط X"""
    try:
        # https://x.com/username -> username
        parts = url.rstrip('/').split('/')
        if len(parts) >= 4 and 'x.com' in url:
            return parts[-1]
        return None
    except Exception as e:
        logger.error(f"❌ خطأ في استخراج اليوزرنيم: {e}")
        return None


def load_x_sources_from_db() -> List[Dict]:
    """تحميل مصادر X من قاعدة البيانات (source_type_id = 7)"""
    try:
        if not db.conn:
            db.connect()
        
        cursor = db.conn.cursor()
        query = """
            SELECT id, url, name, is_active
            FROM public.sources
            WHERE source_type_id = 7 AND is_active = true
            ORDER BY id
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        
        sources = []
        for row in rows:
            source_id = row[0]
            url = row[1]
            name = row[2]
            username = extract_username_from_url(url)
            
            if username:
                sources.append({
                    'id': source_id,
                    'url': url,
                    'name': name,
                    'username': username
                })
        
        logger.info(f"✅ تم تحميل {len(sources)} مصدر X من قاعدة البيانات")
        return sources
    
    except Exception as e:
        logger.error(f"❌ خطأ في تحميل مصادر X: {e}")
        if db.conn:
            db.conn.rollback()
        return []


def extract_media_url(media_item) -> Optional[str]:
    """استخراج رابط الميديا من التغريدة"""
    for attr in ['url', 'media_url_https', 'media_url', 'preview_image_url', 'expanded_url']:
        val = getattr(media_item, attr, None)
        if val and isinstance(val, str) and val.startswith('http'):
            return val
    
    if isinstance(media_item, dict):
        for key in ['url', 'media_url_https', 'media_url']:
            if media_item.get(key):
                return media_item[key]
    
    return None


def extract_image(tweet) -> Optional[str]:
    """استخراج أول صورة من التغريدة"""
    try:
        if hasattr(tweet, 'media') and tweet.media:
            for media_item in tweet.media:
                url = extract_media_url(media_item)
                if url:
                    return url
        
        if hasattr(tweet, '_data'):
            entities = tweet._data.get('entities', {})
            media_list = entities.get('media', [])
            for m in media_list:
                url = m.get('media_url_https') or m.get('media_url')
                if url:
                    return url
    
    except Exception:
        pass
    
    return None


def clean_tweet_text(text: str) -> str:
    """
    تنظيف نص التغريدة من الروابط والهاشتاغات الزائدة
    
    Args:
        text: نص التغريدة الأصلي
    
    Returns:
        النص المنظف
    """
    import re
    
    if not text:
        return text
    
    # إزالة الروابط (https://t.co/...)
    text = re.sub(r'https?://t\.co/\w+', '', text)
    
    # إزالة الروابط العادية
    text = re.sub(r'https?://[^\s]+', '', text)
    
    # إزالة المسافات الزائدة (قبل حذف الهاشتاغات)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # إزالة جميع الهاشتاغات من نهاية النص (واحد أو أكثر، مع أو بدون مسافات أو علامات ترقيم)
    # مثال: .#نشرة_المحافظات#العُمانية أو #عاجل #أخبار
    text = re.sub(r'[.\s]*#[\w_]+(\s*#[\w_]+)*\s*$', '', text)
    
    # إزالة المسافات من البداية والنهاية مرة أخرى
    text = text.strip()
    
    return text


def tweet_to_article(tweet, username: str, source_name: str) -> NewsArticle:
    """تحويل التغريدة إلى NewsArticle"""
    text = getattr(tweet, 'text', '') or getattr(tweet, 'full_text', '')
    tweet_id = str(getattr(tweet, 'id', '') or getattr(tweet, 'id_str', ''))
    
    # تنظيف النص من الروابط والهاشتاغات
    cleaned_text = clean_tweet_text(text)
    
    # تاريخ النشر
    created_at_str = str(getattr(tweet, 'created_at', ''))
    pub_date = None
    try:
        if created_at_str:
            # تحويل التاريخ من صيغة X إلى datetime
            pub_date = datetime.strptime(created_at_str, '%a %b %d %H:%M:%S %z %Y')
    except:
        pub_date = datetime.now()
    
    url = f"https://x.com/{username}/status/{tweet_id}"
    
    return NewsArticle(
        source=source_name,
        title=cleaned_text,  # نفس النص المنظف
        url=url,
        pub_date=pub_date,
        summary=cleaned_text,
        full_text=cleaned_text,
        image_url=extract_image(tweet)
    )


async def setup_client():
    """
    إعداد الكلايت باستخدام X_AUTH_TOKEN و X_CT0_TOKEN من .env
    بدون أي لوجن
    """
    try:
        from twikit import Client
    except ImportError:
        logger.error("❌ twikit غير مثبت. شغّل: pip install twikit")
        exit(1)

    client = Client(language='ar-SA')

    # التحقق من وجود الـ tokens
    if not X_AUTH_TOKEN or not X_CT0_TOKEN:
        raise RuntimeError(
            "❌ X_AUTH_TOKEN أو X_CT0_TOKEN غير موجودة في .env\n"
            "تأكد من إضافة القيم الصحيحة في ملف .env"
        )

    try:
        # إنشاء ملف الكوكيز من الـ tokens
        logger.info("🔑 تحميل الكوكيز من X_AUTH_TOKEN و X_CT0_TOKEN...")
        with open(COOKIES_FILE, "w") as f:
            json.dump({"auth_token": X_AUTH_TOKEN, "ct0": X_CT0_TOKEN}, f)
        
        # تحميل الكوكيز
        client.load_cookies(COOKIES_FILE)
        
        # اختبار سريع للتحقق من صلاحية الكوكيز
        await client.get_user_by_screen_name('twitter')
        logger.info("✅ كوكيز صالحة — تم التحميل بنجاح")
    except Exception as e:
        raise RuntimeError(
            f"❌ فشل تحميل الكوكيز: {str(e)}\n"
            "تأكد من أن X_AUTH_TOKEN و X_CT0_TOKEN صحيحة وصالحة"
        )

    return client


async def scrape_account(client, source: Dict) -> Dict:
    """سحب تغريدات من حساب واحد"""
    username = source['username']
    source_id = source['id']
    source_name = source['name']
    
    tweets_data = []
    status = "unknown"
    error_msg = None
    
    try:
        user = await client.get_user_by_screen_name(username)
        logger.info(f"   👤 {user.name} (@{username}) — {user.followers_count:,} متابع")
        
        tweets = []
        
        # محاولة get_tweets مباشرة (تخطي البحث لتجنب recursion error)
        try:
            tweets = await user.get_tweets('Tweets', count=MAX_TWEETS_PER_ACCOUNT)
            if DEBUG:
                logger.info(f"      [get_tweets] وجدت {len(tweets)} تغريدة")
        except Exception as e2:
            if DEBUG:
                logger.info(f"      [get_tweets فشل] {str(e2)[:60]}")
        
        if not tweets:
            status = "⚠️ بدون تغريدات"
            logger.info(f"   {status}")
            return {"articles": [], "status": status, "error": None}
        
        # تحويل التغريدات إلى NewsArticle
        for idx, tweet in enumerate(tweets):
            try:
                text = getattr(tweet, 'text', '') or getattr(tweet, 'full_text', '')
                if text and len(text.strip()) > 0:
                    article = tweet_to_article(tweet, username, source_name)
                    tweets_data.append(article)
                elif DEBUG:
                    logger.info(f"      [تغريدة فارغة {idx}]")
            except Exception as e:
                if DEBUG:
                    logger.info(f"      [خطأ في التغريدة {idx}] {str(e)[:60]}")
                continue
        
        status = "✅ نجح"
        logger.info(f"   {status} — {len(tweets_data)} تغريدة")
    
    except Exception as e:
        error = str(e)
        if "Rate limit" in error or "429" in error:
            status = "⏳ Rate limit"
            error_msg = "تم تجاوز الحد — انتظر دقيقة"
            logger.info(f"   {status}")
            await asyncio.sleep(60)
        elif "Could not find" in error or "404" in error:
            status = "❌ غير موجود"
            error_msg = "الحساب غير موجود أو محذوف"
            logger.info(f"   {status}: @{username}")
        elif "suspended" in error.lower():
            status = "🚫 موقوف"
            error_msg = "الحساب موقوف من X"
            logger.info(f"   {status}: @{username}")
        elif "Unauthorized" in error or "401" in error:
            status = "🔐 خطأ مصادقة"
            error_msg = "الكوكيز انتهت أو غير صحيحة"
            logger.info(f"   {status}")
        elif "Forbidden" in error or "403" in error:
            status = "🔒 ممنوع"
            error_msg = "لا صلاحية للوصول"
            logger.info(f"   {status}: @{username}")
        else:
            status = "❌ خطأ"
            error_msg = error[:120]
            logger.info(f"   {status}: {error_msg}")
    
    return {"articles": tweets_data, "status": status, "error": error_msg}


async def scrape_and_save_source(client, source: Dict) -> Dict:
    """
    سحب من مصدر واحد ومعالجة وحفظ في raw_news
    
    Returns:
        إحصائيات السحب والحفظ
    """
    source_id = source['id']
    username = source['username']
    
    logger.info(f"\n📡 @{username} (ID: {source_id})")
    
    # سحب التغريدات
    result = await scrape_account(client, source)
    
    articles = result["articles"]
    status = result["status"]
    error = result["error"]
    
    if status != "✅ نجح" or not articles:
        return {
            'source_id': source_id,
            'username': username,
            'status': status,
            'error': error,
            'total_scraped': 0,
            'filtered': 0,
            'saved': 0,
            'skipped': 0,
            'errors': 0,
            'with_numbers': 0,
            'by_language': {}
        }
    
    # معالجة وحفظ المقالات
    stats = ArticleProcessor.process_and_save(source_id, articles)
    
    # إضافة معلومات المصدر
    stats['source_id'] = source_id
    stats['username'] = username
    stats['status'] = status
    stats['error'] = error
    stats['total_scraped'] = len(articles)
    
    return stats


async def scrape_all_x_sources() -> Dict:
    """
    سحب من جميع مصادر X في قاعدة البيانات
    
    Returns:
        إحصائيات شاملة
    """
    logger.info("=" * 60)
    logger.info("🐦 X (Twitter) Scraper - Database Integration")
    logger.info("=" * 60)
    
    # تحميل المصادر
    sources = load_x_sources_from_db()
    
    if not sources:
        logger.error("❌ لا توجد مصادر X في قاعدة البيانات")
        return {}
    
    # إعداد الكلايت
    client = await setup_client()
    
    total_stats = {
        'total_sources': len(sources),
        'total_scraped': 0,
        'total_filtered': 0,
        'total_saved': 0,
        'total_skipped': 0,
        'total_errors': 0,
        'total_with_numbers': 0,
        'by_language': {},
        'by_source': {},
        'failed_sources': []
    }
    
    for i, source in enumerate(sources, 1):
        logger.info(f"\n[{i}/{len(sources)}]")
        
        try:
            stats = await scrape_and_save_source(client, source)
            
            total_stats['total_scraped'] += stats.get('total_scraped', 0)
            total_stats['total_filtered'] += stats.get('filtered', 0)
            total_stats['total_saved'] += stats.get('saved', 0)
            total_stats['total_skipped'] += stats.get('skipped', 0)
            total_stats['total_errors'] += stats.get('errors', 0)
            total_stats['total_with_numbers'] += stats.get('with_numbers', 0)
            
            # تجميع إحصائيات اللغة
            for lang, count in stats.get('by_language', {}).items():
                if lang not in total_stats['by_language']:
                    total_stats['by_language'][lang] = 0
                total_stats['by_language'][lang] += count
            
            total_stats['by_source'][source['id']] = stats
            
            if stats['status'] != "✅ نجح":
                total_stats['failed_sources'].append({
                    'source_id': source['id'],
                    'username': source['username'],
                    'status': stats['status'],
                    'error': stats.get('error')
                })
        
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة المصدر {source['id']}: {e}")
            total_stats['failed_sources'].append({
                'source_id': source['id'],
                'username': source['username'],
                'status': '❌ خطأ',
                'error': str(e)[:120]
            })
        
        # تأخير بين الحسابات
        if i < len(sources):
            await asyncio.sleep(DELAY_BETWEEN_ACCOUNTS)
    
    # ملخص النتائج
    logger.info("\n" + "=" * 60)
    logger.info("📊 ملخص النتائج")
    logger.info("=" * 60)
    logger.info(f"✅ إجمالي التغريدات: {total_stats['total_scraped']}")
    logger.info(f"✅ تم الحفظ: {total_stats['total_saved']}")
    logger.info(f"⏭️  موجودة: {total_stats['total_skipped']}")
    logger.info(f"🔍 تم الفلترة: {total_stats['total_filtered']}")
    logger.info(f"🔢 مع أرقام: {total_stats['total_with_numbers']}")
    logger.info(f"🌐 حسب اللغة: {total_stats['by_language']}")
    
    if total_stats['failed_sources']:
        logger.info(f"\n❌ الحسابات الفاشلة ({len(total_stats['failed_sources'])}):")
        for item in total_stats['failed_sources']:
            err = f" — {item['error']}" if item['error'] else ""
            logger.info(f"  • @{item['username']}: {item['status']}{err}")
    
    logger.info("=" * 60)
    
    return total_stats


async def main():
    """الدالة الرئيسية"""
    try:
        # الاتصال بقاعدة البيانات
        if not db.conn:
            db.connect()
        
        # سحب من جميع المصادر
        stats = await scrape_all_x_sources()
        
        # حفظ الإحصائيات
        output_file = f"x_scraper_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"\n💾 الإحصائيات محفوظة في: {output_file}")
    
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")


if __name__ == "__main__":
    asyncio.run(main())
