"""
API endpoints for translation service
نقاط نهاية API لخدمة الترجمة
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import os
from services.translation.translator import NewsTranslator
from database.connection import DatabaseConnection
from utils.logger import logger

router = APIRouter(prefix="/api/translation", tags=["translation"])


class TranslationRequest(BaseModel):
    """طلب ترجمة نص"""

    text: str
    source_language: Optional[str] = "auto"  # auto, he, en


class TranslationResponse(BaseModel):
    """استجابة الترجمة"""

    original: str
    translated: str
    source_language: str
    target_language: str = "ar"


class BatchTranslationRequest(BaseModel):
    """طلب ترجمة دفعة"""

    texts: List[str]
    source_language: Optional[str] = "auto"


class TranslationStatsResponse(BaseModel):
    """إحصائيات الترجمة"""

    total_translations: int
    pending_articles: int
    by_source_language: dict
    by_target_language: dict


@router.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    ترجمة نص واحد
    Translate a single text
    """
    try:
        api_key = os.getenv("war_news_translation_api_key")
        if not api_key:
            raise HTTPException(status_code=500, detail="API key not configured")

        translator = NewsTranslator(api_key=api_key)
        translation = await translator.translate_single(request.text)

        if not translation:
            raise HTTPException(status_code=500, detail="Translation failed")

        return TranslationResponse(
            original=request.text,
            translated=translation,
            source_language=request.source_language,
        )

    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate-batch")
async def translate_batch(request: BatchTranslationRequest):
    """
    ترجمة دفعة من النصوص
    Translate a batch of texts
    """
    try:
        api_key = os.getenv("war_news_translation_api_key")
        if not api_key:
            raise HTTPException(status_code=500, detail="API key not configured")

        translator = NewsTranslator(api_key=api_key, max_concurrent=5)
        translations = await translator.translate_batch(request.texts)

        results = [
            {
                "original": original,
                "translated": translated,
                "success": translated is not None,
            }
            for original, translated in zip(request.texts, translations)
        ]

        return {
            "total": len(request.texts),
            "successful": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "results": results,
        }

    except Exception as e:
        logger.error(f"Batch translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate-articles")
async def translate_articles(
    raw_news_ids: List[int], background_tasks: BackgroundTasks
):
    """
    ترجمة مقالات من قاعدة البيانات
    Translate articles from database
    """
    try:
        api_key = os.getenv("war_news_translation_api_key")
        if not api_key:
            raise HTTPException(status_code=500, detail="API key not configured")

        # Add translation task to background
        async def translate_task():
            translator = NewsTranslator(api_key=api_key, max_concurrent=5)
            result = await translator.translate_and_store(raw_news_ids)
            logger.info(f"Translation task completed: {result}")

        # Run in background
        background_tasks.add_task(translate_task)

        return {
            "status": "processing",
            "message": f"Translation started for {len(raw_news_ids)} articles",
            "article_ids": raw_news_ids,
        }

    except Exception as e:
        logger.error(f"Article translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=TranslationStatsResponse)
async def get_translation_stats():
    """
    الحصول على إحصائيات الترجمة
    Get translation statistics
    """
    try:
        db = DatabaseConnection()
        if not db.connect():
            raise HTTPException(status_code=500, detail="Database connection failed")

        # Total translations
        db.cursor.execute("SELECT COUNT(*) FROM translations")
        result = db.cursor.fetchone()
        total_translations = result['count'] if isinstance(result, dict) else result[0]

        # Pending articles
        db.cursor.execute(
            """
            SELECT COUNT(*) FROM raw_news
            WHERE language_id IN (2, 3)
            AND processing_status = 0
            """
        )
        result = db.cursor.fetchone()
        pending_articles = result['count'] if isinstance(result, dict) else result[0]

        # By source language
        db.cursor.execute(
            """
            SELECT l.name, COUNT(r.id) as count
            FROM raw_news r
            JOIN languages l ON r.language_id = l.id
            WHERE r.language_id IN (2, 3)
            GROUP BY l.name
            """
        )
        by_source = {}
        for row in db.cursor.fetchall():
            if isinstance(row, dict):
                by_source[row['name']] = row['count']
            else:
                by_source[row[0]] = row[1]

        # By target language
        db.cursor.execute(
            """
            SELECT l.name, COUNT(t.id) as count
            FROM translations t
            JOIN languages l ON t.language_id = l.id
            GROUP BY l.name
            """
        )
        by_target = {}
        for row in db.cursor.fetchall():
            if isinstance(row, dict):
                by_target[row['name']] = row['count']
            else:
                by_target[row[0]] = row[1]

        db.close()

        return TranslationStatsResponse(
            total_translations=total_translations,
            pending_articles=pending_articles,
            by_source_language=by_source,
            by_target_language=by_target,
        )

    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    فحص صحة الخدمة
    Health check for translation service
    """
    try:
        api_key = os.getenv("war_news_translation_api_key")
        if not api_key:
            return {"status": "error", "message": "API key not configured"}

        # Try to connect to database
        db = DatabaseConnection()
        if not db.connect():
            return {"status": "error", "message": "Database connection failed"}

        db.cursor.execute("SELECT 1")
        db.close()

        return {
            "status": "healthy",
            "api_key_configured": True,
            "database_connected": True,
        }

    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"status": "error", "message": str(e)}
