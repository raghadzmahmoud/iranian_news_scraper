"""
معالج أخطاء حفظ المقالات
Article Error Handler
"""
from enum import Enum
from utils.logger import logger


class ArticleSaveStatus(Enum):
    """حالات حفظ المقالة"""
    SUCCESS = "success"  # تم الحفظ بنجاح
    DUPLICATE = "duplicate"  # المقالة موجودة بالفعل (URL مكرر)
    ERROR = "error"  # حدث خطأ في قاعدة البيانات
    INVALID = "invalid"  # بيانات المقالة غير صحيحة


class ArticleErrorHandler:
    """معالج أخطاء حفظ المقالات"""
    
    @staticmethod
    def handle_save_result(result, article_url: str = None) -> ArticleSaveStatus:
        """
        معالجة نتيجة حفظ المقالة
        
        Args:
            result: نتيجة save_article
                - int: معرّف المقالة (نجح)
                - None: المقالة موجودة (Duplicate)
                - False: خطأ في قاعدة البيانات
            article_url: رابط المقالة (للتسجيل)
        
        Returns:
            ArticleSaveStatus: حالة الحفظ
        """
        if isinstance(result, int) and result > 0:
            logger.info(f"✅ تم حفظ المقالة بنجاح - ID: {result}")
            return ArticleSaveStatus.SUCCESS
        
        elif result is None:
            logger.info(f"⏭️  المقالة موجودة بالفعل - URL: {article_url[:60] if article_url else 'N/A'}")
            return ArticleSaveStatus.DUPLICATE
        
        elif result is False:
            logger.error(f"❌ خطأ في حفظ المقالة - URL: {article_url[:60] if article_url else 'N/A'}")
            return ArticleSaveStatus.ERROR
        
        else:
            logger.warning(f"⚠️  نتيجة غير متوقعة: {result}")
            return ArticleSaveStatus.INVALID
    
    @staticmethod
    def handle_batch_results(results: dict) -> str:
        """
        معالجة نتائج حفظ مجموعة من المقالات
        
        Args:
            results: قاموس يحتوي على:
                - 'saved': عدد المقالات المحفوظة
                - 'duplicates': عدد المقالات المكررة
                - 'errors': عدد المقالات التي حدث خطأ عند حفظها
        
        Returns:
            رسالة ملخص النتائج
        """
        saved = results.get('saved', 0)
        duplicates = results.get('duplicates', 0)
        errors = results.get('errors', 0)
        total = saved + duplicates + errors
        
        message = f"""
📊 ملخص حفظ المقالات:
   ✅ تم حفظ: {saved} مقالة
   ⏭️  مكررة: {duplicates} مقالة
   ❌ أخطاء: {errors} مقالة
   📈 الإجمالي: {total} مقالة
        """
        
        logger.info(message)
        return message
    
    @staticmethod
    def should_retry(status: ArticleSaveStatus) -> bool:
        """
        تحديد ما إذا كان يجب إعادة محاولة حفظ المقالة
        
        Args:
            status: حالة الحفظ
        
        Returns:
            True إذا كان يجب إعادة المحاولة
        """
        # لا نعيد محاولة المقالات المكررة أو غير الصحيحة
        return status == ArticleSaveStatus.ERROR
