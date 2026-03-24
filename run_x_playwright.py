#!/usr/bin/env python
"""
Playwright-only entry point for scraping X accounts and saving results via the existing
ArticleProcessor pipeline (avoids the twikit-based client and the need for auth tokens).
"""
import asyncio
import json
from datetime import datetime
from typing import Iterable, List, Tuple

from playwright.async_api import async_playwright

from config.settings import X_DELAY_BETWEEN_ACCOUNTS, X_PLAYWRIGHT_BATCH_SIZE
from storage.article_processor import ArticleProcessor
from storage.news_storage import NewsStorage
from utils.logger import logger
from utils.number_detector import NumberDetector

from scrapers.x_playwright import (
    load_x_sources_from_db,
    load_or_create_session,
    scrape_profile,
)


def normalize_url(url: str) -> str:
    """Normalize URLs so we avoid storing duplicates across runs."""
    if not url:
        return ""
    return url.split("?")[0].split("#")[0]


def chunked(items: List, batch_size: int) -> Iterable[List]:
    """Yield successive batches of the given size."""
    for start in range(0, len(items), batch_size):
        yield items[start:start + batch_size]


def collect_unique_articles(articles: List, seen_urls: set) -> Tuple[List, int, int]:
    """Return articles whose URLs were not previously stored, count duplicates, and reject ones lacking numbers."""
    unique = []
    duplicates = 0
    numbers_filtered = 0
    for article in articles:
        normalized = normalize_url(article.url)
        if not normalized:
            continue
        if normalized in seen_urls:
            duplicates += 1
            continue

        seen_urls.add(normalized)
        if NewsStorage.url_exists(article.url):
            duplicates += 1
            continue
        text = (article.full_text or article.summary or article.title or "").strip()
        has_numbers = NumberDetector.detect_numbers(text, use_war_context=True).get("has_numbers", False)
        if not has_numbers:
            numbers_filtered += 1
            continue

        unique.append(article)

    return unique, duplicates, numbers_filtered


async def run():
    logger.info("=" * 56)
    logger.info("🐦 Playwright-only X scraper (incremental saves)")
    logger.info("=" * 56)

    sources = await load_x_sources_from_db()
    if not sources:
        logger.warning("⚠️ No active X sources found in the database.")
        return

    start_time = datetime.now()
    total_stats = {
        "total_sources": len(sources),
        "total_articles_scraped": 0,
        "total_new_articles": 0,
        "total_saved": 0,
        "total_duplicates": 0,
        "total_numbers_filtered": 0,
        "total_errors": 0,
        "per_source": []
    }

    seen_urls = set()

    async with async_playwright() as pw:
        context, page = await load_or_create_session(pw)

        for idx, source in enumerate(sources, 1):
            handle = f"@{source['username']}"
            logger.info(f"[{idx}/{len(sources)}] {handle} (ID: {source['id']})")

            source_summary = {
                "source_id": source['id'],
                "username": source['username'],
                "scraped": 0,
                "new": 0,
                "saved": 0,
                "duplicates": 0,
                "numbers_filtered": 0,
                "errors": 0,
            }

            try:
                articles = await scrape_profile(page, source)
                source_summary["scraped"] = len(articles)
                total_stats["total_articles_scraped"] += len(articles)

                if not articles:
                    logger.info(f"   ☑️  No tweets found for {handle}")
                    continue

                new_articles, duplicates, numbers_filtered = collect_unique_articles(articles, seen_urls)
                source_summary["duplicates"] += duplicates
                source_summary["numbers_filtered"] = numbers_filtered
                total_stats["total_duplicates"] += duplicates
                total_stats["total_numbers_filtered"] += numbers_filtered

                if not new_articles:
                    logger.info(f"   ☑️  No new tweets to store for {handle}")
                    continue

                source_summary["new"] = len(new_articles)
                total_stats["total_new_articles"] += len(new_articles)

                for batch_idx, batch in enumerate(chunked(new_articles, X_PLAYWRIGHT_BATCH_SIZE), 1):
                    batch_stats = ArticleProcessor.process_and_save(source['id'], batch)
                    source_summary["saved"] += batch_stats.get('saved', 0)
                    source_summary["duplicates"] += batch_stats.get('duplicates', 0)
                    source_summary["errors"] += batch_stats.get('errors', 0)

                    total_stats["total_saved"] += batch_stats.get('saved', 0)
                    total_stats["total_duplicates"] += batch_stats.get('duplicates', 0)
                    total_stats["total_errors"] += batch_stats.get('errors', 0)

                    if batch_stats.get('saved', 0):
                        logger.info(f"   🟢 Batch {batch_idx}: saved {batch_stats.get('saved', 0)} articles (dup {batch_stats.get('duplicates', 0)})")
                    elif batch_stats.get('duplicates', 0):
                        logger.info(f"   ⚠️ Batch {batch_idx}: all duplicates ({batch_stats.get('duplicates', 0)})")
                    elif batch_stats.get('errors', 0):
                        logger.warning(f"   ❌ Batch {batch_idx}: errors saving {batch_stats.get('errors', 0)} articles")

            except Exception as exc:
                logger.error(f"   ❌ Failed to scrape {handle}: {exc}")
                source_summary["errors"] += 1
                total_stats["total_errors"] += 1

            finally:
                total_stats["per_source"].append(source_summary)

            if idx < len(sources):
                await asyncio.sleep(X_DELAY_BETWEEN_ACCOUNTS)

        await context.close()

    total_stats["run_started"] = start_time.isoformat()
    end_time = datetime.now()
    total_stats["run_finished"] = end_time.isoformat()
    total_stats["runtime_seconds"] = (end_time - start_time).total_seconds()

    logger.info("🧮 Finished scraping; writing stats to disk")
    logger.info(f"   ✅ Total saved: {total_stats['total_saved']}")
    logger.info(f"   ⚠️ Total duplicates skipped: {total_stats['total_duplicates']}")
    logger.info(f"   🔢 Total number-filtered articles: {total_stats['total_numbers_filtered']}")
    logger.info(f"   ❌ Total errors: {total_stats['total_errors']}")

    output_file = f"x_playwright_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(total_stats, f, ensure_ascii=False, indent=2, default=str)

    logger.info(f"💾 Stats and processing metadata written to {output_file}")

    return total_stats


if __name__ == "__main__":
    asyncio.run(run())
