import asyncio
import logging
from datetime import datetime
from services.translation.translator import NewsTranslator
from database.connection import DatabaseConnection
import os

logger = logging.getLogger(__name__)


class TranslationJob:
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.api_key = os.getenv("war_news_translation_api_key")

    async def run(self, batch_size: int = 50):
        """Run translation job for pending articles."""
        if not self.api_key:
            logger.error("Translation API key not configured")
            return {"status": "error", "message": "API key missing"}

        translator = NewsTranslator(api_key=self.api_key, max_concurrent=self.max_concurrent)

        db = DatabaseConnection()
        if not db.connect():
            logger.error("Failed to connect to database")
            return {"status": "error", "message": "Database connection failed"}

        try:
            # Get pending articles (language_id 2=Hebrew, 3=English)
            db.cursor.execute(
                """
                SELECT id FROM raw_news
                WHERE language_id IN (2, 3)
                AND processing_status = 0
                AND id NOT IN (
                    SELECT raw_news_id FROM translations
                    WHERE language_id = 1
                )
                LIMIT %s
                """,
                (batch_size,),
            )

            pending_articles = db.cursor.fetchall()
            raw_news_ids = [
                article['id'] if isinstance(article, dict) else article[0]
                for article in pending_articles
            ]

            if not raw_news_ids:
                logger.info("No pending articles to translate")
                return {"status": "success", "translated": 0, "message": "No pending articles"}

            logger.info(f"Starting translation job for {len(raw_news_ids)} articles")

            # Translate and store
            result = await translator.translate_and_store(raw_news_ids, target_language_id=1)

            logger.info(f"Translation job completed: {result}")
            return {"status": "success", **result, "timestamp": datetime.now().isoformat()}

        except Exception as e:
            logger.error(f"Translation job error: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            db.close()


async def run_translation_job():
    """Entry point for translation job."""
    job = TranslationJob(max_concurrent=5)
    return await job.run(batch_size=50)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = asyncio.run(run_translation_job())
    print(result)
