"""
Playwright-based X Scraper - Integrated with DB
Adapted from X_scraper/ for iranian_news_scraper project
"""

import asyncio
import os
import random
import re
from datetime import datetime
from typing import List, Dict
from playwright.async_api import async_playwright
from models.article import NewsArticle
from database.connection import db
from utils.logger import logger
from config.settings import (
    USE_X_PLAYWRIGHT,
    X_USERNAME,
    X_PASSWORD,
    X_CHROME_PROFILE_DIR,
    X_MAX_SCROLLS,
    X_MAX_TWEETS,
    X_PLAYWRIGHT_CHANNEL,
    X_PLAYWRIGHT_HEADLESS,
)

CHROME_PROFILE_DIR = X_CHROME_PROFILE_DIR or os.path.join(os.path.dirname(__file__), "../X_scraper/chrome_profile")

# Stealth args to avoid detection
STEALTH_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-infobars",
    "--no-sandbox",
    "--disable-gpu",
    "--disable-dev-shm-usage",
]

class AuthChallengeError(Exception):
    pass

def parse_credentials():
    """Parse X credentials from env vars"""
    if not X_USERNAME or not X_PASSWORD:
        raise ValueError("X_USERNAME and X_PASSWORD must be set in .env")
    return X_USERNAME, X_PASSWORD

async def load_or_create_session(playwright):
    """Launch persistent Chrome context with auth"""
    needs_login = not os.path.exists(os.path.join(CHROME_PROFILE_DIR, "Default"))

    # Ensure dir exists
    os.makedirs(CHROME_PROFILE_DIR, exist_ok=True)

    launch_kwargs = {
        "user_data_dir": CHROME_PROFILE_DIR,
        "headless": X_PLAYWRIGHT_HEADLESS,
        "args": STEALTH_ARGS,
        "ignore_default_args": ["--enable-automation"],
    }
    if X_PLAYWRIGHT_CHANNEL:
        launch_kwargs["channel"] = X_PLAYWRIGHT_CHANNEL

    context = await playwright.chromium.launch_persistent_context(**launch_kwargs)

    await context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
    """)

    page = context.pages[0] if context.pages else await context.new_page()

    if needs_login:
        await _perform_login(page)
    else:
        # Verify session
        await page.goto("https://x.com/home", timeout=30000)
        if "login" in page.url or "i/flow" in page.url:
            logger.warning("Session expired, re-authenticating...")
            await context.close()
            # Relaunch visible for re-login
            relaunch_kwargs = {
                "user_data_dir": CHROME_PROFILE_DIR,
                "headless": X_PLAYWRIGHT_HEADLESS,
                "args": STEALTH_ARGS,
                "ignore_default_args": ["--enable-automation"],
            }
            if X_PLAYWRIGHT_CHANNEL:
                relaunch_kwargs["channel"] = X_PLAYWRIGHT_CHANNEL

            context = await playwright.chromium.launch_persistent_context(**relaunch_kwargs)
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            """)
            page = context.pages[0] if context.pages else await context.new_page()
            await _perform_login(page)

    logger.info(f"✅ Playwright session ready. Profile: {CHROME_PROFILE_DIR}")
    return context, page

async def _perform_login(page):
    """Perform X login"""
    username, password = parse_credentials()
    
    await page.goto("https://x.com/i/flow/login", timeout=30000)

    # Username
    await page.wait_for_selector('input[autocomplete="username"]', timeout=30000)
    await page.fill('input[autocomplete="username"]', username)
    await page.click('span:has-text("Next")')

    # Handle challenges
    await page.wait_for_timeout(3000)
    pw_selector = 'input[name="password"]'
    if not await page.query_selector(pw_selector):
        challenge = await page.query_selector('input[data-testid="ocfEnterTextTextInput"]')
        if challenge:
            raise AuthChallengeError(
                "X identity verification needed. Complete manually in browser, then re-run."
            )

    # Password
    await page.wait_for_selector(pw_selector, timeout=30000)
    await page.fill(pw_selector, password)
    await page.click('[data-testid="LoginForm_Login_Button"]')

    await page.wait_for_url("**/home", timeout=60000)
    logger.info(f"✅ Logged in as @{username}")

SEL_TWEET = 'article[data-testid="tweet"]'
SEL_TIME = "time[datetime]"
SEL_TWEET_TEXT = '[data-testid="tweetText"]'
SEL_SOCIAL_CTX = '[data-testid="socialContext"]'

async def _extract_tweet_id(article):
    """Extract tweet ID from status link"""
    try:
        links = await article.query_selector_all("a[href*='/status/']")
        for link in links:
            href = await link.get_attribute("href") or ""
            m = re.search(r"/status/(\d+)", href)
            if m:
                return m.group(1)
    except:
        pass
    return None

async def _is_retweet(article):
    """Check if retweet"""
    try:
        ctx = await article.query_selector(SEL_SOCIAL_CTX)
        if ctx:
            text = await ctx.inner_text()
            return "reposted" in (text or "").lower()
    except:
        pass
    return False

async def scrape_profile(page, source: Dict, max_scrolls=None, max_tweets=None):
    """Scrape profile tweets → NewsArticle list"""
    if max_scrolls is None:
        max_scrolls = X_MAX_SCROLLS
    if max_tweets is None:
        max_tweets = X_MAX_TWEETS

    handle = source['username']
    source_id = source['id']
    source_name = source['name']

    articles = []
    seen_ids = set()

    url = f"https://x.com/{handle}"
    await page.goto(url, timeout=30000)

    try:
        await page.wait_for_selector(SEL_TWEET, timeout=30000)
    except:
        logger.warning(f"  [{handle}] No tweets (private/suspended)")
        return []

    logger.info(f"  [{handle}] Scraping...")

    scroll_pause_min = 1500
    scroll_pause_max = 3500

    for scroll_n in range(max_scrolls):
        tweet_elements = await page.query_selector_all(SEL_TWEET)

        new_this_round = 0
        for article in tweet_elements:
            tweet_id = await _extract_tweet_id(article)
            if not tweet_id or tweet_id in seen_ids:
                continue
            seen_ids.add(tweet_id)

            if await _is_retweet(article):
                continue

            time_el = await article.query_selector(SEL_TIME)
            text_el = await article.query_selector(SEL_TWEET_TEXT)
            if not time_el or not text_el:
                continue

            post_time = await time_el.get_attribute("datetime")
            tweet_body = await text_el.inner_text()

            if not post_time or not tweet_body.strip():
                continue

            # Create NewsArticle
            url = f"https://x.com/{handle}/status/{tweet_id}"
            news_article = NewsArticle(
                source=source_name,
                title=tweet_body.strip(),
                url=url,
                pub_date=post_time,
                summary=tweet_body.strip(),
                full_text=tweet_body.strip()
            )

            articles.append(news_article)
            new_this_round += 1

            if len(articles) >= max_tweets:
                break

        if new_this_round == 0 and scroll_n > 0:
            break

        delay = random.randint(scroll_pause_min, scroll_pause_max)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(delay)

    logger.info(f"  [{handle}] {len(articles)} tweets scraped")
    return articles

async def load_x_sources_from_db():
    """Load active X sources (source_type_id=7)"""
    if not db.conn:
        db.connect()
    
    cursor = db.conn.cursor()
    query = """
        SELECT id, url, name, is_active
        FROM public.sources
        WHERE source_type_id = 7 AND is_active = true
        ORDER BY id
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    sources = []
    for row in rows:
        source_id = row[0]
        url = row[1]
        name = row[2]
        username = url.rstrip('/').split('/')[-1].lstrip('@')
        sources.append({'id': source_id, 'url': url, 'name': name, 'username': username})
    
    logger.info(f"✅ Loaded {len(sources)} X sources from DB")
    return sources

async def scrape_all_playwright() -> List[NewsArticle]:
    """Main entry: Scrape all X sources via Playwright"""
    if not USE_X_PLAYWRIGHT:
        raise ValueError("USE_X_PLAYWRIGHT not enabled")

    sources = await load_x_sources_from_db()
    if not sources:
        logger.warning("No X sources in DB")
        return []

    all_articles = []

    async with async_playwright() as pw:
        context = await load_or_create_session(pw)
        page = await context.new_page()

        for source in sources:
            try:
                articles = await scrape_profile(page, source)
                all_articles.extend(articles)

                # Delay between accounts
                if source != sources[-1]:
                    await asyncio.sleep(3)
            except AuthChallengeError:
                logger.error("Auth challenge - manual intervention needed")
                break
            except Exception as e:
                logger.error(f"Error scraping {source['username']}: {e}")

        await context.close()

    return all_articles

