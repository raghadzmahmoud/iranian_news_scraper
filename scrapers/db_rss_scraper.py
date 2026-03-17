"""
سكراب RSS من قاعدة البيانات - نسخة محسّنة
"""
import requests
from bs4 import BeautifulSoup
import feedparser
import asyncio
from datetime import datetime
from email.utils import parsedate_to_datetime
from dateutil import parser as date_parser
from models.article import NewsArticle
from database.connection import db
from storage.news_storage import NewsStorage
from storage.article_processor import ArticleProcessor
from config.settings import HEADERS
from utils.logger import logger


def load_rss_sources_from_db() -> dict:
    """تحميل المصادر من قاعدة البيانات"""
    try:
        if not db.conn:
            db.connect()
        
        cursor = db.conn.cursor()
        query = """
            SELECT s.id, s.url, st.name as type, s.is_active, s.name, s.source_type_id
            FROM public.sources s
            JOIN public.source_types st ON s.source_type_id = st.id
            WHERE s.is_active = true
            ORDER BY st.name, s.id
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        
        sources = {}
        for row in rows:
            source_id = row[0]
            sources[source_id] = {
                'id': source_id,
                'url': row[1],
                'type': row[2],
                'active': row[3],
                'name': row[4],
                'source_type_id': row[5]
            }
        
        logger.info(f"✅ تم تحميل {len(sources)} مصدر من قاعدة البيانات")
        return sources
    
    except Exception as e:
        logger.error(f"❌ خطأ في تحميل المصادر: {e}")
        if db.conn:
            db.conn.rollback()
        return {}


def get_source_type_id_from_db(source_id: int) -> int:
    """الحصول على نوع المصدر (ID) من قاعدة البيانات - 6=RSS, 7=X"""
    try:
        if not db.conn:
            db.connect()
        
        cursor = db.conn.cursor()
        query = """
            SELECT source_type_id
            FROM public.sources
            WHERE id = %s
        """
        cursor.execute(query, (source_id,))
        result = cursor.fetchone()
        cursor.close()
        
        return result[0] if result else -1
    
    except Exception as e:
        logger.error(f"❌ خطأ في الحصول على نوع المصدر: {e}")
        if db.conn:
            db.conn.rollback()
        return -1


def parse_rss_from_db(source_id: int, max_items: int = 10) -> list[NewsArticle]:
    """تحليل RSS من مصدر في قاعدة البيانات"""
    sources = load_rss_sources_from_db()
    
    if source_id not in sources:
        logger.error(f"❌ مصدر غير معروف: {source_id}")
        return []
    
    feed_url = sources[source_id]['url']
    logger.info(f"📡 جاري تحليل RSS من المصدر {source_id}...")
    
    try:
        resp = requests.get(feed_url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        
        feed = feedparser.parse(resp.text)
        
        if not feed.entries:
            logger.warning(f"⚠️  لا توجد مقالات في الـ RSS")
            return []
        
        articles = []
        skipped_count = 0
        
        for entry in feed.entries[:max_items]:
            try:
                title = entry.get('title', 'بدون عنوان')
                url = entry.get('link', '')
                summary = entry.get('summary', '')
                
                # شرط خاص للمصدر 17 (Annahar): تخطي المقالات اللي فيها "opinion" في الـ URL
                if source_id == 17 and 'opinion' in url.lower():
                    logger.info(f"⏭️  تم تخطي مقالة opinion من المصدر 17: {title[:50]}")
                    skipped_count += 1
                    continue
                
                # إزالة الـ HTML tags من الملخص
                if summary:
                    soup = BeautifulSoup(summary, 'html.parser')
                    for img in soup.find_all('img'):
                        img.decompose()
                    summary = soup.get_text(separator=' ', strip=True)
                
                pub_date = None
                # محاولة استخراج تاريخ النشر من عدة حقول
                if entry.get('published_parsed'):
                    pub_date = datetime(*entry.published_parsed[:6])
                elif entry.get('updated_parsed'):
                    pub_date = datetime(*entry.updated_parsed[:6])
                elif entry.get('pubDate'):
                    # محاولة تحليل pubDate كنص
                    try:
                        pub_date = parsedate_to_datetime(entry.get('pubDate'))
                    except:
                        pub_date = None
                elif entry.get('dc_date'):
                    # محاولة تحليل dc:date (من DW وغيرها)
                    try:
                        pub_date = date_parser.parse(entry.get('dc_date'))
                    except:
                        pub_date = None
                elif entry.get('date'):
                    # محاولة تحليل date العام
                    try:
                        pub_date = date_parser.parse(entry.get('date'))
                    except:
                        pub_date = None
                
                if not pub_date:
                    logger.warning(f"⚠️  لم يتم العثور على تاريخ نشر للمقالة: {title[:50]}")
                
                article = NewsArticle(
                    title=title,
                    url=url,
                    summary=summary,
                    source=f"Source {source_id}",
                    pub_date=pub_date
                )
                
                articles.append(article)
            
            except Exception as e:
                logger.warning(f"⚠️  خطأ في معالجة مقالة: {e}")
                continue
        
        logger.info(f"✅ تم تحليل {len(articles)} مقالة من RSS")
        if skipped_count > 0:
            logger.info(f"⏭️  تم تخطي {skipped_count} مقالة opinion من المصدر 17")
        return articles
    
    except Exception as e:
        logger.error(f"❌ خطأ في تحليل الـ RSS: {e}")
        return []


def scrape_full_article_from_db(article: NewsArticle, source_id: int) -> NewsArticle:
    """سحب الخبر الكامل من الموقع"""
    if not article.url:
        logger.warning(f"⚠️  لا يوجد رابط للمقالة")
        return article
    
    try:
        resp = requests.get(article.url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        
        soup = BeautifulSoup(resp.text, "lxml")
        
        # إزالة العناصر غير المرغوبة
        remove_selectors = [
            "div[class*='advertisement']", "div[class*='ad-']",
            "div[class*='taboola']", "div[class*='outbrain']",
            "nav", "aside", "footer",
            "div[class*='sidebar']", "div[class*='related']",
            "div[class*='share']", "div[class*='social']",
            "div[class*='comment']", "script", "style", "noscript"
        ]
        
        for selector in remove_selectors:
            for el in soup.select(selector):
                el.decompose()
        
        # البحث عن محتوى المقال
        article_selectors = [
            "article", "main",
            "div.article-body", "div.article-content",
            "div[data-testid='article-body']",
            "div[itemprop='articleBody']"
        ]
        
        article_body = None
        for selector in article_selectors:
            article_body = soup.select_one(selector)
            if article_body:
                break
        
        if not article_body:
            divs = soup.find_all("div")
            if divs:
                article_body = max(divs, key=lambda d: len(d.get_text(strip=True)))
        
        if article_body:
            paragraphs = []
            for p in article_body.find_all("p"):
                text = p.get_text(separator=" ", strip=True)
                if text and len(text) > 30:
                    paragraphs.append(text)
            
            if paragraphs:
                article.full_text = "\n\n".join(paragraphs)
                article.paragraphs = paragraphs
            else:
                article.full_text = article_body.get_text(separator="\n", strip=True)
            
            # استخراج الصورة
            if not article.image_url:
                img_tag = article_body.find("img")
                if img_tag:
                    img_src = img_tag.get("src") or img_tag.get("data-src")
                    if img_src and img_src.startswith("http"):
                        article.image_url = img_src
        
        article.scraping_type = "full_scrape"
        word_count = len(article.full_text.split()) if article.full_text else 0
        logger.info(f"✅ تم سحب الخبر الكامل: {word_count} كلمة")
        
    except Exception as e:
        logger.error(f"❌ خطأ في سحب الخبر الكامل: {e}")
        article.scraping_type = "rss_only"
    
    return article


def smart_scrape_from_db(source_id: int, max_items: int = 10) -> list[NewsArticle]:
    """سحب ذكي من قاعدة البيانات بناءً على نوع المصدر (ID 6=RSS, ID 7=X)"""
    import asyncio
    from scrapers.x_scraper import setup_client, scrape_account

    sources = load_rss_sources_from_db()

    if source_id not in sources:
        logger.error(f"❌ مصدر غير معروف: {source_id}")
        return []

    source = sources[source_id]
    source_type_id = source.get('source_type_id')

    logger.info(f"🔍 سحب ذكي من المصدر {source_id} ({source['name']}) - نوع: {source_type_id}")

    # إذا كان المصدر من نوع X (ID=7)
    if source_type_id == 7:
        logger.info(f"🐦 سحب من X/Twitter للمصدر {source_id}")
        try:
            # استخراج اسم المستخدم من الـ URL
            url = source['url']
            username = url.split('/')[-1]

            # إنشء source dict للـ X scraper
            x_source = {
                'id': source_id,
                'username': username,
                'name': source['name'],
                'url': url
            }

            # تشغيل الـ async scraper
            async def scrape_x():
                client = await setup_client()
                result = await scrape_account(client, x_source)
                return result.get('articles', [])

            # تشغيل الـ async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            articles = loop.run_until_complete(scrape_x())
            loop.close()

            logger.info(f"✅ تم سحب {len(articles)} تغريدة من X")
            return articles[:max_items]
        except Exception as e:
            logger.error(f"❌ خطأ في سحب X: {e}")
            return []

    # إذا كان المصدر من نوع RSS (ID=6) أو أي نوع آخر
    articles = parse_rss_from_db(source_id, max_items=max_items)

    logger.info(f"📝 سحب من RSS")
    for article in articles:
        article.scraping_type = "rss_only"

    return articles



def smart_scrape_and_save(source_id: int, max_items: int = 10) -> dict:
    """
    سحب ذكي وحفظ في قاعدة البيانات مع الفلترة والمعالجة
    
    Args:
        source_id: معرّف المصدر
        max_items: عدد المقالات
    
    Returns:
        قاموس بإحصائيات السحب والحفظ والمعالجة
    """
    logger.info(f"🚀 بدء السحب والمعالجة والحفظ من المصدر {source_id}")
    
    # السحب الذكي
    articles = smart_scrape_from_db(source_id, max_items=max_items)
    
    if not articles:
        logger.warning(f"⚠️  لم يتم جلب أي مقالات")
        return {
            'source_id': source_id,
            'total_scraped': 0,
            'total_filtered': 0,
            'total_saved': 0,
            'total_skipped': 0,
            'total_errors': 0,
            'total_with_numbers': 0,
            'by_language': {}
        }
    
    logger.info(f"📰 تم جلب {len(articles)} مقالة")
    
    # معالجة وحفظ المقالات
    stats = ArticleProcessor.process_and_save(source_id, articles)
    
    # إضافة معلومات المصدر
    stats['source_id'] = source_id
    stats['total_scraped'] = len(articles)
    
    return stats


def scrape_all_sources_and_save(max_items: int = 10) -> dict:
    """
    سحب من جميع المصادر وحفظ في قاعدة البيانات مع الفلترة والمعالجة
    
    Args:
        max_items: عدد المقالات من كل مصدر
    
    Returns:
        إحصائيات شاملة
    """
    logger.info(f"🚀 بدء السحب من جميع المصادر")
    
    sources = load_rss_sources_from_db()
    
    if not sources:
        logger.error(f"❌ لا توجد مصادر")
        return {}
    
    total_stats = {
        'total_sources': len(sources),
        'total_scraped': 0,
        'total_filtered': 0,
        'total_saved': 0,
        'total_skipped': 0,
        'total_errors': 0,
        'total_with_numbers': 0,
        'by_language': {},
        'by_source': {}
    }
    
    for source_id in sources.keys():
        try:
            stats = smart_scrape_and_save(source_id, max_items=max_items)
            
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
            
            total_stats['by_source'][source_id] = stats
        
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة المصدر {source_id}: {e}")
    
    logger.info(f"✅ انتهى السحب من جميع المصادر")
    logger.info(f"   📊 إجمالي: {total_stats['total_scraped']} مقالة")
    logger.info(f"   🔍 تم الفلترة: {total_stats['total_filtered']}")
    logger.info(f"   💾 محفوظة: {total_stats['total_saved']}")
    logger.info(f"   ⏭️  موجودة: {total_stats['total_skipped']}")
    logger.info(f"   ❌ أخطاء: {total_stats['total_errors']}")
    logger.info(f"   🔢 مع أرقام: {total_stats['total_with_numbers']}")
    logger.info(f"   🌐 حسب اللغة: {total_stats['by_language']}")
    
    return total_stats
