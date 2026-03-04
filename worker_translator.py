import asyncio
import os
import logging
from services.translation.translator import NewsTranslator
from database.connection import DatabaseConnection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def translate_pending_articles():
    """Fetch pending articles and translate them."""
    api_key = os.getenv("war_news_translation_api_key")
    if not api_key:
        logger.error("API key not found in environment variables")
        return

    translator = NewsTranslator(api_key=api_key, max_concurrent=5)

    # Get pending articles (language_id 2=Hebrew, 3=English)
    db = DatabaseConnection()
    if not db.connect():
        logger.error("Failed to connect to database")
        return

    try:
        db.cursor.execute(
            """
            SELECT id FROM raw_news
            WHERE language_id IN (2, 3)
            AND processing_status = 0
            LIMIT 50
            """
        )
        pending_articles = db.cursor.fetchall()
        raw_news_ids = [
            article['id'] if isinstance(article, dict) else article[0]
            for article in pending_articles
        ]

        if not raw_news_ids:
            logger.info("No pending articles to translate")
            return

        logger.info(f"Found {len(raw_news_ids)} articles to translate")

        # Translate and store
        result = await translator.translate_and_store(raw_news_ids)
        logger.info(f"Translation result: {result}")

    except Exception as e:
        logger.error(f"Error in translate_pending_articles: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(translate_pending_articles())
