import asyncio
import logging
from typing import List, Optional
import aiohttp
from database.connection import DatabaseConnection

logger = logging.getLogger(__name__)

TRANSLATION_SYSTEM_PROMPT = """You are a professional translator specializing in Hebrew and English to Arabic translation for a leading Arabic news station focused on economics and politics.

Your Role:
- Translate Hebrew and English news articles to Modern Standard Arabic
- Maintain the highest level of professionalism
- Preserve accuracy and journalistic tone

Target Audience:
- Specialized, professional audience
- Experts in politics, security, and economics

Coverage Focus:
- Israeli internal affairs
- News, security, and economic developments
- Iran-related news

MANDATORY Terminology Rules (CRITICAL):

Hebrew Terms:
- Replace "צבא ההגנה" (Army of Defense) with "الجيش الإسرائيلي" (Israeli Army)
- Replace "מחבל" (terrorist/saboteur) with "مسلح" (armed person)
- Replace "כוחות הכיבוש" (Occupation Forces) with "الجيش الإسرائيلي" (Israeli Army)
- Replace "מוסד" (Mossad) with "الموساد"
- Replace "שב״כ" (Shin Bet) with "جهاز الشاباك"
- Replace "מבצע" (Operation) with "عملية عسكرية"

English Terms:
- Replace "IDF / Israel Defense Forces" with "الجيش الإسرائيلي" (Israeli Army)
- Replace "Terrorist" with "مسلح" (armed person)
- Replace "Occupation Forces" with "الجيش الإسرائيلي" (Israeli Army)
- Replace "Airstrike / Air raid" with "غارة جوية"
- Replace "Ceasefire" with "وقف إطلاق النار"
- Replace "Casualties" with "ضحايا" or "إصابات" based on context
- Replace "Senior official" with "مسؤول رفيع"
- Replace "Sources familiar with" with "مصادر مطلعة على"

Translation Guidelines:
- Use professional journalistic Arabic (Al Jazeera / Al Arabiya standard)
- Preserve proper nouns (names, places, organizations)
- Maintain factual accuracy
- Keep the original meaning and context
- Maintain complete neutrality - no bias toward any party
- Output ONLY the Arabic translation, no explanations

IMPORTANT: The translation must be completely neutral and unbiased."""


class NewsTranslator:
    def __init__(self, api_key: str, max_concurrent: int = 5):
        self.api_key = api_key
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.base_url = "https://api.openai.com/v1/chat/completions"

    async def translate_single(self, text: str) -> Optional[str]:
        """Translate a single article with semaphore for bounded concurrency."""
        async with self.semaphore:
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    }
                    payload = {
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": TRANSLATION_SYSTEM_PROMPT},
                            {
                                "role": "user",
                                "content": f"Translate this news article to Arabic:\n\n{text}",
                            },
                        ],
                        "temperature": 0.2,
                        "max_tokens": 3000,
                    }

                    async with session.post(
                        self.base_url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=60)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data["choices"][0]["message"]["content"].strip()
                        else:
                            error_text = await response.text()
                            logger.error(f"API error {response.status}: {error_text}")
                            return None
            except asyncio.TimeoutError:
                logger.error("Translation request timeout")
                return None
            except Exception as e:
                logger.error(f"Translation error: {e}")
                return None

    async def translate_batch(self, texts: List[str]) -> List[Optional[str]]:
        """Translate multiple articles with bounded concurrency."""
        tasks = [self.translate_single(text) for text in texts]
        return await asyncio.gather(*tasks)

    async def translate_and_store(
        self, raw_news_ids: List[int], target_language_id: int = 1
    ) -> dict:
        """
        Fetch articles from DB, translate them, and store translations.
        
        Args:
            raw_news_ids: List of raw_news IDs to translate
            target_language_id: Language ID for target (1 = Arabic)
        
        Returns:
            Dictionary with success/failure counts
        """
        from database.connection import db
        
        try:
            db.ensure_connection()
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return {"success": 0, "failed": len(raw_news_ids), "error": "Database connection failed"}

        try:
            # Fetch articles that need translation
            placeholders = ",".join(["%s"] * len(raw_news_ids))
            cursor = db.conn.cursor()
            cursor.execute(
                f"""
                SELECT id, title_original, content_original, language_id
                FROM raw_news
                WHERE id IN ({placeholders})
                AND language_id IN (2, 3)
                AND processing_status = 0
                """,
                raw_news_ids,
            )

            articles = cursor.fetchall()
            cursor.close()
            
            if not articles:
                logger.info("No articles to translate")
                return {"success": 0, "failed": 0, "skipped": len(raw_news_ids)}

            # Prepare texts for translation
            # إرسال العنوان والمحتوى بشكل منفصل للترجمة
            articles_data = []
            for article in articles:
                if isinstance(article, dict):
                    articles_data.append({
                        'id': article['id'],
                        'title': article['title_original'],
                        'content': article['content_original'],
                        'lang_id': article['language_id']
                    })
                else:
                    articles_data.append({
                        'id': article[0],
                        'title': article[1],
                        'content': article[2],
                        'lang_id': article[3]
                    })
            
            # ترجمة العناوين والمحتوى بشكل منفصل
            titles_to_translate = [a['title'] for a in articles_data]
            contents_to_translate = [a['content'] for a in articles_data]
            
            logger.info(f"Starting translation of {len(articles_data)} articles")

            # Translate with bounded concurrency
            translated_titles = await self.translate_batch(titles_to_translate)
            translated_contents = await self.translate_batch(contents_to_translate)

            # Store translations in database
            success_count = 0
            failed_count = 0
            updated_status_count = 0

            for article_data, translated_title, translated_content in zip(articles_data, translated_titles, translated_contents):
                raw_news_id = article_data['id']

                if not translated_title or not translated_content:
                    failed_count += 1
                    continue

                # تنظيف الترجمة من البادئات غير المرغوبة
                translated_title = translated_title.strip()
                translated_content = translated_content.strip()
                
                # إزالة البادئات إذا كانت موجودة
                if translated_title.startswith("Title:"):
                    translated_title = translated_title.replace("Title:", "", 1).strip()
                if translated_title.startswith("العنوان:"):
                    translated_title = translated_title.replace("العنوان:", "", 1).strip()
                
                if translated_content.startswith("Content:"):
                    translated_content = translated_content.replace("Content:", "", 1).strip()
                if translated_content.startswith("المحتوى:"):
                    translated_content = translated_content.replace("المحتوى:", "", 1).strip()

                try:
                    # Check if translation already exists
                    cursor = db.conn.cursor()
                    cursor.execute(
                        """
                        SELECT id FROM translations
                        WHERE raw_news_id = %s AND language_id = %s
                        """,
                        (raw_news_id, target_language_id),
                    )

                    existing = cursor.fetchone()

                    if existing:
                        # Update existing translation
                        cursor.execute(
                            """
                            UPDATE translations
                            SET title = %s, content = %s
                            WHERE raw_news_id = %s AND language_id = %s
                            """,
                            (
                                translated_title,
                                translated_content,
                                raw_news_id,
                                target_language_id,
                            ),
                        )
                    else:
                        # Insert new translation
                        cursor.execute(
                            """
                            INSERT INTO translations (raw_news_id, language_id, title, content)
                            VALUES (%s, %s, %s, %s)
                            """,
                            (
                                raw_news_id,
                                target_language_id,
                                translated_title,
                                translated_content,
                            ),
                        )

                    # Update processing_status to 1 (true) after successful translation
                    # 1 = جاهز للنشر (Ready for publishing)
                    cursor.execute(
                        """
                        UPDATE raw_news
                        SET processing_status = 1
                        WHERE id = %s
                        """,
                        (raw_news_id,),
                    )
                    
                    # التحقق من أن التحديث تم بنجاح
                    if cursor.rowcount > 0:
                        updated_status_count += 1
                        logger.info(f"✅ تم حفظ الترجمة للخبر {raw_news_id} وتحديث الحالة إلى 1 (جاهز للنشر)")
                    else:
                        logger.warning(f"⚠️  لم يتم تحديث الحالة للخبر {raw_news_id}")

                    cursor.close()
                    success_count += 1

                except Exception as e:
                    logger.error(f"Failed to store translation for {raw_news_id}: {e}")
                    failed_count += 1

            db.conn.commit()
            logger.info(
                f"✅ انتهت الترجمة: {success_count} نجح، {failed_count} فشل، {updated_status_count} تم تحديث الحالة"
            )
            return {"success": success_count, "failed": failed_count, "status_updated": updated_status_count, "total": len(articles)}

        except Exception as e:
            logger.error(f"Translation batch error: {e}")
            db.conn.rollback()
            return {"success": 0, "failed": len(raw_news_ids), "error": str(e)}
        finally:
            db.close()
