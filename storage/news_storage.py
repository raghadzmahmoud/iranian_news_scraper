"""
موديول تخزين واسترجاع الأخبار من قاعدة البيانات
"""
import psycopg2
from datetime import datetime
from database.connection import db
from utils.logger import logger


class NewsStorage:
    """فئة لإدارة تخزين واسترجاع الأخبار"""
    
    @staticmethod
    def get_language_id(language_code: str) -> int:
        """الحصول على معرّف اللغة"""
        try:
            if not db.conn:
                db.connect()
            
            cursor = db.conn.cursor()
            query = "SELECT id FROM public.languages WHERE code = %s"
            cursor.execute(query, (language_code,))
            result = cursor.fetchone()
            cursor.close()
            
            return result[0] if result else 1  # الافتراضي: عربي
        
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على معرّف اللغة: {e}")
            if db.conn:
                db.conn.rollback()
            return 1
    
    @staticmethod
    def url_exists(url: str) -> bool:
        """التحقق من وجود URL في قاعدة البيانات"""
        try:
            if not db.conn:
                db.connect()
            
            cursor = db.conn.cursor()
            
            # تنظيف URL من المعاملات الإضافية
            clean_url = url.split('?')[0].split('#')[0] if url else ""
            
            # البحث عن URL دقيق أو URL بدون معاملات
            query = """
                SELECT 1 FROM public.raw_news 
                WHERE url = %s 
                OR url LIKE %s
                LIMIT 1
            """
            cursor.execute(query, (url, clean_url + '%'))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                logger.info(f"⏭️  URL موجود بالفعل: {url[:60]}")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"❌ خطأ في التحقق من URL: {e}")
            if db.conn:
                db.conn.rollback()
            return False
    
    @staticmethod
    def save_article(source_id: int, article_data: dict) -> int:
        """
        حفظ مقالة في قاعدة البيانات
        
        Args:
            source_id: معرّف المصدر
            article_data: بيانات المقالة {title, url, content, language, published_at, has_numbers}
        
        Returns:
            معرّف المقالة المحفوظة أو None
        
        ملاحظة:
            processing_status يتم تعيينه تلقائياً بناءً على اللغة:
            - 1 = عربي أصلي (جاهز للنشر)
            - 0 = أجنبي (يحتاج ترجمة)
            
            بعد الترجمة، يتم تحديثه إلى 1 باستخدام update_translated_status_job
        """
        try:
            if not db.conn:
                db.connect()
            
            cursor = db.conn.cursor()
            
            # الحصول على معرّف اللغة
            language_code = article_data.get('language', 'ar')
            language_id = NewsStorage.get_language_id(language_code)
            
            # الحصول على URL
            url = article_data.get('url', '')
            if not url:
                logger.warning(f"⚠️  المقالة بدون URL")
                return None
            
            # التحقق من وجود URL
            if NewsStorage.url_exists(url):
                logger.info(f"⏭️  المقالة موجودة بالفعل: {url[:50]}")
                return None
            
            # الحصول على has_numbers
            has_numbers = article_data.get('has_numbers', False)
            
            # تحديد processing_status بناءً على اللغة
            # 1 = عربي أصلي أو مترجم (جاهز للنشر)
            # 0 = أجنبي (يحتاج ترجمة)
            processing_status = 1 if language_code == 'ar' else 0
            
            # إدراج المقالة
            query = """
                INSERT INTO public.raw_news 
                (source_id, url, title_original, content_original, language_id, published_at, fetched_at, processing_status, has_numbers)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            
            cursor.execute(query, (
                source_id,
                url,
                article_data.get('title', ''),
                article_data.get('content', ''),
                language_id,
                article_data.get('published_at'),
                datetime.now(),
                processing_status,  # 1 للعربي، 0 للأجنبي
                has_numbers
            ))
            
            result = cursor.fetchone()
            db.conn.commit()
            
            if result:
                article_id = result[0]
                logger.info(f"✅ تم حفظ المقالة برقم: {article_id} - URL: {url[:50]}")
                return article_id
            
            return None
        
        except psycopg2.IntegrityError as e:
            db.conn.rollback()
            logger.warning(f"⏭️  المقالة موجودة بالفعل (Integrity Error): {str(e)[:50]}")
            return None
        
        except Exception as e:
            db.conn.rollback()
            logger.error(f"❌ خطأ في حفظ المقالة: {e}")
            return None
        
        finally:
            if cursor:
                cursor.close()
    
    @staticmethod
    def save_articles_batch(source_id: int, articles: list) -> int:
        """
        حفظ مجموعة من المقالات
        
        Args:
            source_id: معرّف المصدر
            articles: قائمة المقالات
        
        Returns:
            عدد المقالات المحفوظة
        """
        saved_count = 0
        
        for article in articles:
            article_data = {
                'title': article.title,
                'url': article.url,
                'content': article.full_text or article.summary,
                'language': getattr(article, 'language', 'ar'),
                'published_at': article.pub_date
            }
            
            if NewsStorage.save_article(source_id, article_data):
                saved_count += 1
        
        return saved_count
    
    @staticmethod
    def get_articles_by_source(source_id: int, limit: int = 10) -> list:
        """الحصول على أخبار من مصدر معين"""
        try:
            if not db.conn:
                db.connect()
            
            cursor = db.conn.cursor()
            query = """
                SELECT id, source_id, url, title_original, content_original, language_id, published_at, fetched_at
                FROM public.raw_news
                WHERE source_id = %s
                ORDER BY fetched_at DESC
                LIMIT %s
            """
            
            cursor.execute(query, (source_id, limit))
            results = cursor.fetchall()
            cursor.close()
            
            return results
        
        except Exception as e:
            logger.error(f"❌ خطأ في جلب الأخبار: {e}")
            return []
    
    @staticmethod
    def get_unprocessed_articles(limit: int = 100) -> list:
        """الحصول على أخبار لم تتم معالجتها"""
        try:
            if not db.conn:
                db.connect()
            
            cursor = db.conn.cursor()
            query = """
                SELECT id, source_id, url, title_original, content_original, language_id, published_at
                FROM public.raw_news
                WHERE processing_status = 0
                ORDER BY fetched_at DESC
                LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            cursor.close()
            
            return results
        
        except Exception as e:
            logger.error(f"❌ خطأ في جلب الأخبار غير المعالجة: {e}")
            return []
    
    @staticmethod
    def update_processing_status(article_id: int, status: int) -> bool:
        """تحديث حالة معالجة المقالة"""
        try:
            if not db.conn:
                db.connect()
            
            cursor = db.conn.cursor()
            query = "UPDATE public.raw_news SET processing_status = %s WHERE id = %s"
            cursor.execute(query, (status, article_id))
            db.conn.commit()
            cursor.close()
            
            return True
        
        except Exception as e:
            db.conn.rollback()
            logger.error(f"❌ خطأ في تحديث حالة المعالجة: {e}")
            return False
    
    @staticmethod
    def get_stats() -> dict:
        """الحصول على إحصائيات الأخبار"""
        try:
            if not db.conn:
                db.connect()
            
            cursor = db.conn.cursor()
            
            # إجمالي الأخبار
            cursor.execute("SELECT COUNT(*) FROM public.raw_news")
            total = cursor.fetchone()[0]
            
            # الأخبار غير المعالجة
            cursor.execute("SELECT COUNT(*) FROM public.raw_news WHERE processing_status = 0")
            unprocessed = cursor.fetchone()[0]
            
            # الأخبار حسب اللغة
            cursor.execute("""
                SELECT l.code, COUNT(rn.id)
                FROM public.raw_news rn
                JOIN public.languages l ON rn.language_id = l.id
                GROUP BY l.code
            """)
            by_language = dict(cursor.fetchall())
            
            cursor.close()
            
            return {
                'total': total,
                'unprocessed': unprocessed,
                'by_language': by_language
            }
        
        except Exception as e:
            logger.error(f"❌ خطأ في جلب الإحصائيات: {e}")
            return {}
