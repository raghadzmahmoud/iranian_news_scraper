"""
وظيفة تحديث حالة الأخبار الأجنبية المترجمة
يتم تشغيلها بشكل دوري للتحقق من الأخبار المترجمة وتحديث حالتها
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from config.settings import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT
from utils.logger import logger


class UpdateTranslatedStatusJob:
    """وظيفة تحديث حالة الأخبار المترجمة"""
    
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
                port=DB_PORT,
                sslmode='require'
            )
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            return True
        except psycopg2.Error as e:
            logger.error(f"❌ خطأ في الاتصال: {e}")
            return False
    
    def get_translated_news_count(self):
        """الحصول على عدد الأخبار المترجمة بحاجة إلى تحديث"""
        try:
            query = """
                SELECT COUNT(DISTINCT rn.id) as count
                FROM public.raw_news rn
                LEFT JOIN public.translations t ON rn.id = t.raw_news_id
                WHERE rn.language_id != (SELECT id FROM languages WHERE code = 'ar')
                AND t.title IS NOT NULL
                AND t.content IS NOT NULL
                AND rn.processing_status = 0
            """
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            return result['count'] if result else 0
        except psycopg2.Error as e:
            logger.error(f"❌ خطأ في عد الأخبار: {e}")
            return 0
    
    def update_translated_news(self):
        """تحديث حالة الأخبار الأجنبية المترجمة"""
        try:
            # الحصول على عدد الأخبار قبل التحديث
            count_before = self.get_translated_news_count()
            
            if count_before == 0:
                logger.info("⚠️  لا توجد أخبار أجنبية مترجمة بحاجة إلى تحديث")
                return {
                    "success": True,
                    "updated": 0,
                    "message": "لا توجد أخبار بحاجة إلى تحديث"
                }
            
            logger.info(f"📊 وجدت {count_before} خبر أجنبي مترجم")
            
            # تحديث processing_status إلى 1
            update_query = """
                UPDATE public.raw_news
                SET processing_status = 1
                WHERE id IN (
                    SELECT rn.id
                    FROM public.raw_news rn
                    LEFT JOIN public.translations t ON rn.id = t.raw_news_id
                    WHERE rn.language_id != (SELECT id FROM languages WHERE code = 'ar')
                    AND t.title IS NOT NULL
                    AND t.content IS NOT NULL
                    AND rn.processing_status = 0
                )
            """
            
            self.cursor.execute(update_query)
            updated_count = self.cursor.rowcount
            self.conn.commit()
            
            logger.info(f"✅ تم تحديث {updated_count} خبر أجنبي مترجم")
            
            return {
                "success": True,
                "updated": updated_count,
                "message": f"تم تحديث {updated_count} خبر بنجاح"
            }
            
        except psycopg2.Error as e:
            logger.error(f"❌ خطأ في التحديث: {e}")
            if self.conn:
                self.conn.rollback()
            return {
                "success": False,
                "updated": 0,
                "error": str(e)
            }
    
    def close(self):
        """إغلاق الاتصال"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


def run_update_translated_status_job():
    """تشغيل وظيفة التحديث"""
    job = UpdateTranslatedStatusJob()
    
    try:
        if not job.connect():
            logger.error("❌ فشل الاتصال بقاعدة البيانات")
            return False
        
        result = job.update_translated_news()
        logger.info(f"📋 نتيجة التحديث: {result}")
        return result['success']
        
    finally:
        job.close()


if __name__ == "__main__":
    run_update_translated_status_job()
