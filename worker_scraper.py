"""
Worker منفصل لمعالجة الـ Scraping Jobs
Scraper Worker - يعمل كل 10 دقايق
"""
import time
import threading
import random
from datetime import datetime
from database.connection import DatabaseConnection
from utils.logger import logger
from main import scrape_all_news, scrape_telegram_sources, save_telegram_posts_to_db


class ScraperWorker:
    """Worker لمعالجة الـ Scraping Jobs"""
    
    def __init__(self, interval=600):  # 600 ثانية = 10 دقايق
        self.running = False
        self.thread = None
        self.interval = interval
        self.db = None  # سيتم إنشاؤه في الـ thread
    
    def start(self):
        """بدء الـ Worker"""
        if self.running:
            logger.warning("⚠️ Scraper Worker قيد التشغيل بالفعل")
            return
        
        self.running = True
        logger.info(f"✅ تم بدء Scraper Worker (كل {self.interval} ثانية)")
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
    
    def _run(self):
        """حلقة التشغيل الرئيسية"""
        while self.running:
            try:
                self.run_once()
            except Exception as e:
                logger.error(f"❌ خطأ في حلقة الـ Scraper: {e}")
            
            # الانتظار قبل الدورة التالية
            for _ in range(self.interval):
                if not self.running:
                    break
                time.sleep(1)
    
    def stop(self):
        """إيقاف الـ Worker"""
        self.running = False
        if self.db:
            self.db.close()
        logger.info("🛑 تم إيقاف Scraper Worker")
    
    def run_once(self):
        """تشغيل دورة واحدة من الـ Scraper"""
        try:
            # إنشاء connection منفصلة
            db = DatabaseConnection()
            if not db.connect():
                logger.error("❌ فشل الاتصال بقاعدة البيانات")
                return False
            
            logger.info("✅ تم الاتصال بقاعدة البيانات بنجاح")
            logger.info(f"📰 جاري تشغيل Scraper Job في {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # ========================================
            # Step 1: سحب الأخبار من RSS
            # ========================================
            logger.info("📰 جاري سحب الأخبار من RSS...")
            try:
                from config.keywords import is_relevant_article, get_matching_keywords
                
                rss_articles = scrape_all_news(db_connection=db)
                if rss_articles:
                    logger.info(f"✅ تم سحب {len(rss_articles)} مقالة من RSS")
                    # حفظ المقالات في قاعدة البيانات
                    saved_count = 0
                    failed_count = 0
                    filtered_count = 0
                    for i, article in enumerate(rss_articles, 1):
                        try:
                            # فلترة المقالة قبل الحفظ
                            is_relevant = is_relevant_article(article.title, article.full_text or article.summary, language="he")
                            
                            if not is_relevant:
                                filtered_count += 1
                                logger.info(f"🚫 تم تصفية ({i}/{len(rss_articles)}): {article.title[:50]}... (غير ذي صلة)")
                                continue
                            
                            # الحصول على الكلمات المفتاحية المطابقة
                            matched_keywords = get_matching_keywords(article.title, article.full_text or article.summary, language="he")
                            
                            # تحويل NewsArticle إلى dict للحفظ
                            article_data = {
                                "url": article.url,
                                "full_text": article.full_text or article.summary,
                                "summary": article.summary,
                                "pub_date": article.pub_date,
                                "fetched_at": datetime.now(),
                                "image_url": article.image_url,
                                "tags": matched_keywords if matched_keywords else article.tags
                            }
                            
                            # البحث عن source_id الصحيح حسب نوع المصدر
                            source_id = self._get_source_id_for_rss(db)
                            
                            result = db.insert_raw_data(source_id, article_data)
                            if result:
                                saved_count += 1
                                logger.info(f"💾 تم حفظ ({i}/{len(rss_articles)}): {article.title[:50]}...")
                            else:
                                logger.info(f"⏭️ مقال موجود ({i}/{len(rss_articles)}): {article.title[:50]}...")
                        except Exception as e:
                            failed_count += 1
                            logger.error(f"❌ خطأ في حفظ المقال ({i}/{len(rss_articles)}): {e}")
                            # إعادة تعيين الـ transaction بعد الخطأ
                            try:
                                db.conn.rollback()
                            except:
                                pass
                    
                    logger.info(f"📊 نتائج الحفظ: ✅ {saved_count} نجح، ❌ {failed_count} فشل، 🚫 {filtered_count} تم تصفيتها من أصل {len(rss_articles)} مقالة")
                else:
                    logger.info("ℹ️ لا توجد أخبار جديدة من RSS")
            except Exception as e:
                logger.error(f"❌ خطأ في سحب أخبار RSS: {e}")
            
            # ========================================
            # Step 2: سحب البوستات من Telegram
            # ========================================
            logger.info("📱 جاري سحب البوستات من Telegram...")
            try:
                telegram_posts = scrape_telegram_sources(max_posts=30, db_connection=db)
                if telegram_posts:
                    logger.info(f"✅ تم سحب {len(telegram_posts)} بوست من Telegram")
                    # حفظ البوستات في قاعدة البيانات
                    save_telegram_posts_to_db(telegram_posts, filter_enabled=True, db_connection=db)
                else:
                    logger.info("ℹ️ لا توجد بوستات جديدة من Telegram")
            except Exception as e:
                logger.error(f"❌ خطأ في سحب بوستات Telegram: {e}")
            
            logger.info(f"✅ انتهت دورة الـ Scraping في {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            db.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ خطأ في Scraper run_once: {e}")
            return False
    
    def _get_source_id_for_rss(self, db):
        """الحصول على source_id للـ RSS (افتراضي = 1)"""
        try:
            # البحث عن أول مصدر RSS نشط
            db.cursor.execute("""
                SELECT id FROM public.sources 
                WHERE source_type_id = 1 AND is_active = true 
                LIMIT 1
            """)
            result = db.cursor.fetchone()
            if result:
                source_id = result['id'] if isinstance(result, dict) else result[0]
                logger.info(f"✅ وجدت مصدر RSS برقم: {source_id}")
                return source_id
            else:
                logger.warning("⚠️ لم يتم العثور على مصدر RSS نشط، استخدام ID افتراضي (1)")
                return 1
        except Exception as e:
            logger.error(f"❌ خطأ في البحث عن source_id: {e}")
            # إعادة تعيين الـ transaction بعد الخطأ
            try:
                db.conn.rollback()
            except:
                pass
            return 1


def main():
    """تشغيل الـ Scraper Worker"""
    logger.info("📰 جاري بدء Scraper Worker...")
    
    # بدء الـ Worker
    worker = ScraperWorker(interval=600)  # 10 دقايق
    worker.start()
    
    try:
        logger.info("✅ Scraper Worker يعمل الآن...")
        # الاستمرار في التشغيل
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 جاري إيقاف Scraper Worker...")
        worker.stop()
        logger.info("✅ تم إيقاف Scraper Worker")


if __name__ == "__main__":
    main()
