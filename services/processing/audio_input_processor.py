"""
خدمة معالجة الملفات الصوتية
Audio Input Processing Service
"""
import os
import json
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from database.connection import db
from utils.logger import logger
from config.settings import (
    MAX_AUDIO_SIZE_MB, ALLOWED_AUDIO_FORMATS, S3_BUCKET_NAME, AWS_REGION, 
    S3_ORIGINAL_AUDIOS_FOLDER, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
)


class AudioInputProcessor:
    """معالج الملفات الصوتية"""
    
    SOURCE_TYPE_ID = 5  # user_input
    SOURCE_ID = 5      # voice
    
    # صيغ الملفات المدعومة
    SUPPORTED_FORMATS = {
        'audio/mpeg': '.mp3',
        'audio/wav': '.wav',
        'audio/webm': '.webm',
        'audio/ogg': '.ogg',
        'audio/flac': '.flac'
    }
    
    MAX_FILE_SIZE = MAX_AUDIO_SIZE_MB * 1024 * 1024
    
    @staticmethod
    def process_audio(file_path: str, file_name: str, content_type: str, user_id: int = None) -> dict:
        """
        معالجة الملف الصوتي
        
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
            if content_type not in AudioInputProcessor.SUPPORTED_FORMATS:
                return {
                    "success": False,
                    "error": "نوع ملف غير مدعوم",
                    "message": f"الصيغ المدعومة: {', '.join(AudioInputProcessor.SUPPORTED_FORMATS.keys())}"
                }
            
            # التحقق من حجم الملف
            file_size = os.path.getsize(file_path)
            if file_size > AudioInputProcessor.MAX_FILE_SIZE:
                return {
                    "success": False,
                    "error": "حجم الملف كبير جدًا",
                    "message": f"الحد الأقصى: {AudioInputProcessor.MAX_FILE_SIZE / (1024*1024):.0f} MB"
                }
            
            # رفع الملف إلى S3
            s3_url = AudioInputProcessor._upload_to_s3(file_path, file_name)
            if not s3_url:
                return {
                    "success": False,
                    "error": "فشل الرفع إلى S3",
                    "message": "حدث خطأ أثناء رفع الملف"
                }
            
            # حفظ بيانات الملف
            uploaded_file_id = AudioInputProcessor._save_uploaded_file_metadata(
                file_name=file_name,
                s3_url=s3_url,
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
            
            logger.info(f"✅ تم رفع الملف الصوتي بنجاح: {file_name}")
            
            return {
                "success": True,
                "data": {
                    "uploaded_file_id": uploaded_file_id,
                    "audio_url": s3_url,
                    "message": "تم رفع الملف بنجاح. سيتم معالجته في الخلفية."
                }
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة الملف الصوتي: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "حدث خطأ في معالجة الملف"
            }
    
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
            
            # تحديد مسار الملف في S3
            s3_key = f"{S3_ORIGINAL_AUDIOS_FOLDER}{file_name}"
            
            # رفع الملف
            s3_client.upload_file(
                file_path,
                S3_BUCKET_NAME,
                s3_key,
                ExtraArgs={'ContentType': 'audio/mpeg'}
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
    def _save_uploaded_file_metadata(file_name: str, s3_url: str, content_type: str, 
                                     file_size: int, user_id: int = None) -> int:
        """
        حفظ بيانات الملف المرفوع
        
        Args:
            file_name: اسم الملف
            s3_url: رابط الملف على S3
            content_type: نوع المحتوى
            file_size: حجم الملف
            user_id: معرف المستخدم
            
        Returns:
            int: معرف السجل المحفوظ
        """
        try:
            # إنشاء جدول uploaded_files إذا لم يكن موجودًا
            create_table_query = """
                CREATE TABLE IF NOT EXISTS public.uploaded_files (
                    id BIGSERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    s3_url TEXT NOT NULL,
                    content_type VARCHAR(50),
                    file_size BIGINT,
                    user_id INTEGER,
                    status VARCHAR(50) DEFAULT 'pending',
                    transcription TEXT,
                    processed_at TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """
            db.cursor.execute(create_table_query)
            db.conn.commit()
            
            # إدراج البيانات
            query = """
                INSERT INTO public.uploaded_files 
                (filename, s3_url, content_type, file_size, user_id, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            
            db.cursor.execute(query, (
                file_name,
                s3_url,
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
    def get_audio_status(uploaded_file_id: int) -> dict:
        """
        الحصول على حالة معالجة الملف الصوتي
        
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
