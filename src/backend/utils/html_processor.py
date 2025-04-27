import hashlib
import logging
import redis
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# --- Redis Config ---
redis_client = redis.Redis(host="localhost", port=6379, db=0)

# --- Logging Config ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HTMLCacheUtil")

# --- Constants ---
CACHE_TTL = 3600  # 1 hour
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

def _hash_url(url: str) -> str:
    return hashlib.md5(url.encode("utf-8")).hexdigest()

def _is_html(content_type: str) -> bool:
    return "text/html" in content_type.lower()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=8))
def _fetch_static_html(url: str) -> str:
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    if not _is_html(response.headers.get("Content-Type", "")):
        raise ValueError("Content is not HTML")
    return response.text

def _fetch_dynamic_html(url: str) -> str:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=USER_AGENT)
            page = context.new_page()
            page.goto(url, timeout=15000)  # 15 sec timeout
            page.wait_for_load_state("networkidle", timeout=10000)
            html = page.content()
            browser.close()
            return html
    except PlaywrightTimeoutError as e:
        logger.warning(f"Dynamic load timeout: {e}")
        raise
    except Exception as e:
        logger.error(f"Playwright error: {e}")
        raise

def _clean_html(html: str) -> str:
    try:
        soup = BeautifulSoup(html, "html.parser")
        return soup.prettify()
    except Exception as e:
        logger.warning(f"HTML cleanup failed: {e}")
        return html

def _needs_dynamic_rendering(html: str) -> bool:
    soup = BeautifulSoup(html, "html.parser")
    text_length = len(soup.get_text(strip=True))
    if text_length < 200 or not soup.find():  # page might be empty or JS-based
        logger.info("Suspecting dynamic content, switching to dynamic rendering.")
        return True
    return False

def get_or_fetch_html(url: str) -> str:
    key = f"html:{_hash_url(url)}"

    # Check cache
    cached_html = redis_client.get(key)
    if cached_html:
        logger.info(f"Cache hit for: {url}")
        return cached_html.decode("utf-8")

    # First try static fetch
    try:
        html = _fetch_static_html(url)
        if _needs_dynamic_rendering(html):
            raise ValueError("Content seems dynamic")
    except Exception as static_error:
        logger.warning(f"Static fetch failed or detected dynamic: {static_error}")
        try:
            html = _fetch_dynamic_html(url)
        except Exception as dynamic_error:
            logger.error(f"Failed to fetch HTML from both methods: {dynamic_error}")
            raise dynamic_error

    cleaned_html = _clean_html(html)
    redis_client.setex(key, CACHE_TTL, cleaned_html)
    logger.info(f"Fetched and cached HTML for: {url}")
    return cleaned_html
