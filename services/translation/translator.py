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
        db = DatabaseConnection()
        if not db.connect():
            logger.error("Failed to connect to database")
            return {"success": 0, "failed": len(raw_news_ids), "error": "Database connection failed"}

        try:
            # Fetch articles that need translation
            placeholders = ",".join(["%s"] * len(raw_news_ids))
            db.cursor.execute(
                f"""
                SELECT id, title_original, content_original, language_id
                FROM raw_news
                WHERE id IN ({placeholders})
                AND language_id IN (2, 3)
                AND processing_status = 0
                """,
                raw_news_ids,
            )

            articles = db.cursor.fetchall()
            if not articles:
                logger.info("No articles to translate")
                return {"success": 0, "failed": 0, "skipped": len(raw_news_ids)}

            # Prepare texts for translation
            texts_to_translate = [
                f"Title: {article['title_original']}\n\nContent: {article['content_original']}" 
                if isinstance(article, dict)
                else f"Title: {article[1]}\n\nContent: {article[2]}"
                for article in articles
            ]

            logger.info(f"Starting translation of {len(texts_to_translate)} articles")

            # Translate with bounded concurrency
            translations = await self.translate_batch(texts_to_translate)

            # Store translations in database
            success_count = 0
            failed_count = 0

            for article, translation in zip(articles, translations):
                # Handle both dict and tuple formats
                if isinstance(article, dict):
                    raw_news_id = article['id']
                    title_original = article['title_original']
                    content_original = article['content_original']
                    lang_id = article['language_id']
                else:
                    raw_news_id, title_original, content_original, lang_id = article

                if not translation:
                    failed_count += 1
                    continue

                # Parse translated title and content
                parts = translation.split("\n\n", 1)
                translated_title = (
                    parts[0].replace("Title: ", "").strip() if len(parts) > 0 else ""
                )
                translated_content = parts[1].strip() if len(parts) > 1 else ""

                try:
                    # Check if translation already exists
                    db.cursor.execute(
                        """
                        SELECT id FROM translations
                        WHERE raw_news_id = %s AND language_id = %s
                        """,
                        (raw_news_id, target_language_id),
                    )

                    existing = db.cursor.fetchone()

                    if existing:
                        # Update existing translation
                        db.cursor.execute(
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
                        db.cursor.execute(
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
                    db.cursor.execute(
                        """
                        UPDATE raw_news
                        SET processing_status = 1
                        WHERE id = %s
                        """,
                        (raw_news_id,),
                    )

                    success_count += 1
                    logger.info(f"Stored translation for raw_news_id: {raw_news_id} and marked as processed")

                except Exception as e:
                    logger.error(f"Failed to store translation for {raw_news_id}: {e}")
                    failed_count += 1

            db.conn.commit()
            logger.info(
                f"Translation complete: {success_count} success, {failed_count} failed"
            )
            return {"success": success_count, "failed": failed_count, "total": len(articles)}

        except Exception as e:
            logger.error(f"Translation batch error: {e}")
            db.conn.rollback()
            return {"success": 0, "failed": len(raw_news_ids), "error": str(e)}
        finally:
            db.close()
