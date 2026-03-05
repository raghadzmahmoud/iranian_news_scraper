"""
اختبار وظيفة تحديث حالة الأخبار المترجمة
"""
import sys
from jobs.update_translated_status_job import run_update_translated_status_job
from utils.logger import logger


def test_update_translated_status():
    """اختبار تحديث حالة الأخبار المترجمة"""
    logger.info("🧪 بدء اختبار تحديث حالة الأخبار المترجمة...")
    
    try:
        result = run_update_translated_status_job()
        
        if result:
            logger.info("✅ نجح الاختبار")
            return True
        else:
            logger.error("❌ فشل الاختبار")
            return False
            
    except Exception as e:
        logger.error(f"❌ خطأ في الاختبار: {e}")
        return False


if __name__ == "__main__":
    success = test_update_translated_status()
    sys.exit(0 if success else 1)
