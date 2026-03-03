"""
خدمة معالجة الملفات الفيديو
Video Input Processing Service
"""
import os
import json
import subprocess
import tempfile
from typing import Optional
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from database.connection import db
from utils.logger import logger
from config.settings import (
    MAX_VIDEO_SIZE_MB, ALLOWED_VIDEO_FORMATS, S3_BUCKET_NAME, AWS_REGION, 
    S3_ORIGINAL_VIDEOS_FOLDER, S3_ORIGINAL_AUDIOS_FOLDER, 
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
)


class VideoInputProcessor:
    """معالج الملفات الفيديو"""
    
    SOURCE_TYPE_ID = 5  # user_input
    SOURCE_ID = 6      # video
    
    # صيغ الملفات المدعومة
    SUPPORTED_FORMATS = {
        'video/mp4': '.mp4',
        'video/webm': '.webm',
        'video/quicktime': '.mov',
        'video/x-msvideo': '.avi',
        'video/x-matroska': '.mkv'
    }
    
    MAX_FILE_SIZE = MAX_VIDEO_SIZE_MB * 1024 * 1024
    
    @staticmethod
    def process_video(file_path: str, file_name: str, content_type: str, user_id: int = None) -> dict:
        """
        معالجة الملف الفيديو - رفع فقط
        
        الـ Flow:
        1. التحقق من الملف
        2. رفع الفيديو إلى S3
        3. حفظ معلومات الملف في uploaded_files
        4. الـ job لاحقاً سيستخرج الصوت ويحوله لنص
        
        Args:
            file_path: مسار الملف المؤقت
            file_name: اسم الملف
            content_type: نوع المحتوى (MIME type)
            user_id: معرف المستخدم
            
        Returns:
            dict: نتيجة المعالجة
        """
        try:
            # التحقق من نوع الملف
            if content_type not in VideoInputProcessor.SUPPORTED_FORMATS:
                return {
                    "success": False,
                    "error": "نوع ملف غير مدعوم",
                    "message": f"الصيغ المدعومة: {', '.join(VideoInputProcessor.SUPPORTED_FORMATS.keys())}"
                }
            
            # التحقق من حجم الملف
            file_size = os.path.getsize(file_path)
            if file_size > VideoInputProcessor.MAX_FILE_SIZE:
                return {
                    "success": False,
                    "error": "حجم الملف كبير جدًا",
                    "message": f"الحد الأقصى: {VideoInputProcessor.MAX_FILE_SIZE / (1024*1024):.0f} MB"
                }
            
            # رفع الفيديو إلى S3
            video_s3_url = VideoInputProcessor._upload_to_s3(file_path, file_name)
            if not video_s3_url:
                return {
                    "success": False,
                    "error": "فشل الرفع إلى S3",
                    "message": "حدث خطأ أثناء رفع الملف"
                }
            
            # حفظ بيانات الملف في uploaded_files
            uploaded_file_id = VideoInputProcessor._save_uploaded_file_metadata(
                file_name=file_name,
                video_s3_url=video_s3_url,
                content_type=content_type,
                file_size=file_size,
                user_id=user_id
            )
            
            if not uploaded_file_id:
                return {
                    "success": False,
                    "error": "فشل في حفظ البيانات",
                    "message": "حدث خطأ أثناء حفظ بيانات الملف"
                }
            
            logger.info(f"✅ تم رفع الملف الفيديو بنجاح: {file_name} (ID: {uploaded_file_id})")
            
            return {
                "success": True,
                "message": "تم رفع الملف بنجاح. سيتم تحليل المحتوى في الخلفية للتحقق من ارتباطه بالأحداث الجارية. في حال عدم وجود صلة، لن يتم حفظه ضمن النظام.",
                "data": {
                    "uploaded_file_id": uploaded_file_id,
                    "video_url": video_s3_url
                }
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة الملف الفيديو: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "حدث خطأ في معالجة الملف"
            }
    
    @staticmethod
    def _extract_audio_from_video(video_file_path: str) -> Optional[str]:
        """
        استخراج الصوت من الفيديو باستخدام FFmpeg
        
        Args:
            video_file_path: مسار ملف الفيديو
            
        Returns:
            str: مسار ملف الصوت المستخرج، أو None إذا فشل
        """
        try:
            # تحميل static_ffmpeg إذا كان متاحاً
            try:
                import static_ffmpeg
                static_ffmpeg.add_paths()
            except ImportError:
                pass
            
            import subprocess
            
            # إنشاء مسار مؤقت للملف الصوتي
            output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.wav').name
            
            # أمر FFmpeg لاستخراج الصوت
            cmd = [
                'ffmpeg', '-y', '-i', video_file_path,
                '-vn',               # بدون فيديو
                '-ar', '16000',      # 16kHz sample rate (WhatsApp PTT)
                '-ac', '1',          # mono
                '-acodec', 'pcm_s16le',  # LINEAR16
                output_path
            ]
            
            logger.info(f"🎬 استخراج الصوت من الفيديو: {video_file_path}")
            result = subprocess.run(cmd, capture_output=True, timeout=120, text=True)
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                if file_size > 1000:  # على الأقل 1KB
                    logger.info(f"✅ تم استخراج الصوت: {output_path} ({file_size / 1024:.1f} KB)")
                    return output_path
            
            logger.error(f"❌ فشل استخراج الصوت: {result.stderr}")
            return None
            
        except Exception as e:
            logger.error(f"❌ خطأ في استخراج الصوت: {e}")
            return None
    
    @staticmethod
    def _upload_to_s3(file_path: str, file_name: str) -> str:
        """
        رفع الملف إلى S3 باستخدام AWS SDK
        
        Args:
            file_path: مسار الملف المحلي
            file_name: اسم الملف
            
        Returns:
            str: S3 URI للملف (s3://bucket/path/file)
        """
        try:
            # إنشاء S3 client
            s3_client = boto3.client(
                's3',
                region_name=AWS_REGION,
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
            
            # تحديد المجلد بناءً على نوع الملف
            if file_name.endswith(('.mp4', '.webm', '.mov', '.avi', '.mkv')):
                folder = S3_ORIGINAL_VIDEOS_FOLDER
                content_type = 'video/mp4'
            else:
                folder = S3_ORIGINAL_AUDIOS_FOLDER
                content_type = 'audio/wav'
            
            # تحديد مسار الملف في S3
            s3_key = f"{folder}{file_name}"
            
            # رفع الملف
            s3_client.upload_file(
                file_path,
                S3_BUCKET_NAME,
                s3_key,
                ExtraArgs={'ContentType': content_type}
            )
            
            # إرجاع S3 URI
            s3_uri = f"s3://{S3_BUCKET_NAME}/{s3_key}"
            logger.info(f"✅ تم رفع الملف إلى S3: {s3_uri}")
            return s3_uri
            
        except ClientError as e:
            logger.error(f"❌ خطأ AWS في رفع الملف إلى S3: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ خطأ في رفع الملف إلى S3: {e}")
            return None
    
    @staticmethod
    def _save_uploaded_file_metadata(file_name: str, video_s3_url: str, content_type: str, 
                                     file_size: int, user_id: int = None) -> int:
        """
        حفظ بيانات الملف المرفوع
        
        Args:
            file_name: اسم الملف
            video_s3_url: رابط الفيديو على S3
            content_type: نوع المحتوى
            file_size: حجم الملف
            user_id: معرف المستخدم
            
        Returns:
            int: معرف السجل المحفوظ
            
        ملاحظة:
            - نحفظ video_s3_url في s3_url column
            - الـ job لاحقاً سيستخرج الصوت من الفيديو ويحوله لنص
        """
        try:
            # إدراج البيانات
            query = """
                INSERT INTO public.uploaded_files 
                (filename, s3_url, content_type, file_size, user_id, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            
            db.cursor.execute(query, (
                file_name,
                video_s3_url,  # حفظ رابط الفيديو
                content_type,
                file_size,
                user_id,
                "pending",
                datetime.utcnow()
            ))
            
            result = db.cursor.fetchone()
            db.conn.commit()
            
            if result:
                uploaded_file_id = result['id'] if isinstance(result, dict) else result[0]
                logger.info(f"✅ تم حفظ بيانات الملف برقم: {uploaded_file_id}")
                return uploaded_file_id
            
            return None
            
        except Exception as e:
            logger.error(f"❌ خطأ في حفظ بيانات الملف: {e}")
            db.conn.rollback()
            return None
    
    @staticmethod
    def get_video_status(uploaded_file_id: int) -> dict:
        """
        الحصول على حالة معالجة الملف الفيديو
        
        Args:
            uploaded_file_id: معرف الملف المرفوع
            
        Returns:
            dict: حالة المعالجة
        """
        try:
            query = """
                SELECT id, filename, status, transcription, processed_at
                FROM public.uploaded_files
                WHERE id = %s
            """
            
            db.cursor.execute(query, (uploaded_file_id,))
            result = db.cursor.fetchone()
            
            if result:
                return {
                    "success": True,
                    "data": {
                        "uploaded_file_id": result['id'],
                        "filename": result['filename'],
                        "status": result['status'],
                        "transcription": result['transcription'],
                        "processed_at": result['processed_at'].isoformat() if result['processed_at'] else None
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "الملف غير موجود",
                    "message": f"لم يتم العثور على الملف برقم {uploaded_file_id}"
                }
            
        except Exception as e:
            logger.error(f"❌ خطأ في جلب حالة الملف: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "حدث خطأ في جلب حالة الملف"
            }
