"""
اتصال قاعدة البيانات
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from config.settings import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT
from utils.logger import logger


class DatabaseConnection:
    """إدارة اتصال قاعدة البيانات"""

    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        """الاتصال بقاعدة البيانات"""
        try:
            self.conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                port=DB_PORT
            )
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            logger.info("✅ تم الاتصال بقاعدة البيانات بنجاح")
            return True
        except psycopg2.Error as e:
            logger.error(f"❌ خطأ في الاتصال بقاعدة البيانات: {e}")
            return False

    def get_sources(self):
        """جلب المصادر من قاعدة البيانات"""
        try:
            self.cursor.execute("SELECT id, url, active FROM public.sources WHERE is_active = true")
            sources = self.cursor.fetchall()
            logger.info(f"✅ تم جلب {len(sources)} مصدر من قاعدة البيانات")
            return sources
        except psycopg2.Error as e:
            logger.error(f"❌ خطأ في جلب المصادر: {e}")
            return []

    def get_telegram_sources(self):
        """جلب مصادر Telegram من قاعدة البيانات"""
        try:
            self.cursor.execute(
                """SELECT id, source_type_id, url, is_active 
                   FROM public.sources 
                   WHERE source_type_id = 3 AND is_active = true"""
            )
            sources = self.cursor.fetchall()
            logger.info(f"✅ تم جلب {len(sources)} مصدر Telegram من قاعدة البيانات")
            return sources
        except psycopg2.Error as e:
            logger.error(f"❌ خطأ في جلب مصادر Telegram: {e}")
            return []

    def url_exists(self, url: str) -> bool:
        """التحقق من وجود URL في قاعدة البيانات"""
        try:
            self.cursor.execute("SELECT 1 FROM public.raw_data WHERE url = %s LIMIT 1", (url,))
            result = self.cursor.fetchone()
            return result is not None
        except psycopg2.Error as e:
            logger.error(f"❌ خطأ في التحقق من URL: {e}")
            return False

    def update_article_relevance(self, raw_data_id: int, is_relevant: bool, matched_keywords: list = None):
        """تحديث حالة الصلة والكلمات المفتاحية للمقالة"""
        try:
            keywords_str = ",".join(matched_keywords) if matched_keywords else None
            
            # إذا كان العمود موجود، نحدثه
            query = """
                UPDATE public.raw_data 
                SET tags = %s
                WHERE id = %s
            """
            self.cursor.execute(query, (keywords_str, raw_data_id))
            self.conn.commit()
            return True
        except psycopg2.Error as e:
            logger.error(f"❌ خطأ في تحديث الصلة: {e}")
            self.conn.rollback()
            return False

    def insert_raw_data(self, source_id: int, article_data: dict):
        """إدراج البيانات الخام في جدول raw_data"""
        try:
            # دمج النص الكامل والملخص
            content = article_data.get("full_text") or article_data.get("summary", "")
            
            query = """
                INSERT INTO public.raw_data 
                (source_id, url, content, published_at, fetched_at, is_processed, 
                 media_url, stt_status, source_type_id, tags)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING
                RETURNING id
            """
            self.cursor.execute(query, (
                source_id,
                article_data.get("url"),
                content,
                article_data.get("pub_date"),
                article_data.get("fetched_at"),
                False,  # is_processed
                article_data.get("image_url"),
                "not_needed",  # stt_status - نصوص فقط، لا تحتاج speech-to-text
                1,  # source_type_id (RSS)
                ",".join(article_data.get("tags", [])) if article_data.get("tags") else None,
            ))
            
            result = self.cursor.fetchone()
            self.conn.commit()
            
            if result:
                row_id = result['id'] if isinstance(result, dict) else result[0]
                logger.info(f"✅ تم إدراج البيانات الخام برقم: {row_id}")
                return row_id
            else:
                logger.info(f"⚠️  المقالة موجودة بالفعل: {article_data.get('url')}")
                return None
            
        except psycopg2.Error as e:
            logger.error(f"❌ خطأ في إدراج البيانات الخام: {e}")
            self.conn.rollback()
            return None

    def close(self):
        """إغلاق الاتصال"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("🔌 تم إغلاق الاتصال بقاعدة البيانات")


# Instance واحد للاستخدام في التطبيق
db = DatabaseConnection()
