import logging
import os
import time
from typing import List
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

# Load variables from a .env file in this folder, if present. Values already
# set in the shell (via $env: or export) still take priority over .env.
load_dotenv()

# 1. SETUP LOGGING & CONFIGURATION
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# FIX: this now points at the actual book catalogue, not the toscrape.com
# landing page. The landing page has no article.product_pod elements, so
# the original URL scraped 0 books every run.
BOOK_SITE_START = "https://books.toscrape.com/index.html"
TARGET_COUNT = 60
REQUEST_DELAY = 1.0  # 1-second politeness throttle
MAX_RETRIES = 3

USER_AGENT = "PoliteDataScraperBot/1.0 (+contact: you@example.com)"

# Exact local endpoint pathways mapped from your main.py layout
API_BASE_URL = "http://127.0.0.1:8000"
API_LOGIN_URL = f"{API_BASE_URL}/auth/login"
API_INGEST_URL = f"{API_BASE_URL}/tasks"

# FIX: credentials no longer live in the file. Set these before running:
#   export API_USER_EMAIL="you@example.com"
#   export API_USER_PASSWORD="your-password"
# If you had real credentials hardcoded here before, rotate that password —
# treat it as compromised the moment it touched a file that could be shared
# or committed.
API_USER_EMAIL = os.environ.get("API_USER_EMAIL")
API_USER_PASSWORD = os.environ.get("API_USER_PASSWORD")


# 2. DEFINE THE DATA VALIDATION SENTRY (PYDANTIC)
class BookSchema(BaseModel):
    title: str = Field(..., min_length=1)
    price: float = Field(..., gt=0.0)
    rating: int = Field(..., ge=1, le=5)
    availability: bool


# 3. TEXT SANITIZATION HELPERS
def parse_rating(classes: List[str]) -> int:
    mapping = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    for cls in classes:
        if cls in mapping:
            return mapping[cls]
    return 0


def parse_price(price_str: str) -> float:
    cleaned = "".join(c for c in price_str if c.isdigit() or c == ".")
    return float(cleaned) if cleaned else 0.0


def parse_availability(availability_str: str) -> bool:
    return "in stock" in availability_str.lower()


# 4. ROBOTS.TXT CHECK — added. Refuses to scrape if disallowed or unreadable.
def check_robots_allowed(start_url: str) -> bool:
    robots_url = urljoin(start_url, "/robots.txt")
    parser = RobotFileParser()
    parser.set_url(robots_url)
    try:
        parser.read()
    except Exception as e:
        logging.error(f"Could not read robots.txt at {robots_url}: {e}. Refusing to proceed.")
        return False

    allowed = parser.can_fetch(USER_AGENT, start_url)
    logging.info(f"robots.txt check for {start_url}: {'ALLOWED' if allowed else 'DISALLOWED'}")
    return allowed


# 5. SECURE HANDSHAKE (MATCHES YOUR USERAUTHSCHEMA RULES)
def get_auth_token() -> str:
    """Logs into your API using JSON payload matching your UserAuthSchema blueprint."""
    if not API_USER_EMAIL or not API_USER_PASSWORD:
        raise SystemExit(
            "Missing API_USER_EMAIL / API_USER_PASSWORD environment variables. "
            "Set them before running, e.g.:\n"
            "  export API_USER_EMAIL='you@example.com'\n"
            "  export API_USER_PASSWORD='your-password'"
        )

    logging.info("Attempting authentication handshake with backend API...")
    payload = {"email": API_USER_EMAIL, "password": API_USER_PASSWORD}

    try:
        response = requests.post(API_LOGIN_URL, json=payload, timeout=5)
        if not response.ok:
            # Show the server's actual reason (e.g. "Email not confirmed",
            # "Invalid login credentials") instead of just "401 Unauthorized".
            logging.critical(f"Login rejected ({response.status_code}): {response.text}")
            raise SystemExit(1)
        token = response.json().get("access_token")
        if not token:
            raise ValueError("Authentication response did not include an access_token.")
        logging.info("Authentication successful. Bearer Token acquired safely.")
        return token
    except requests.RequestException as e:
        logging.critical(f"Security Alert: Could not reach the backend API at all. Error: {e}")
        raise SystemExit(e)


def polite_get(url: str, headers: dict) -> requests.Response | None:
    """GET with retry + backoff instead of giving up the whole run on one hiccup."""
    backoff = 2.0
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logging.warning(f"Request failed ({attempt}/{MAX_RETRIES}) for {url}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(backoff)
                backoff *= 2
    logging.error(f"Giving up on {url} after {MAX_RETRIES} attempts.")
    return None


# 6. CORE SCRAPER AND DATA INGESTION ENGINE
def run_secure_pipeline():
    if not check_robots_allowed(BOOK_SITE_START):
        logging.critical("robots.txt disallows this page (or couldn't be read). Stopping.")
        raise SystemExit(1)

    token = get_auth_token()

    public_headers = {"User-Agent": USER_AGENT}
    private_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    scraped_count = 0
    current_url = BOOK_SITE_START

    logging.info("Polite pipeline initialized. Respecting site rules and throttling traffic.")

    while current_url and scraped_count < TARGET_COUNT:
        logging.info(f"Extracting raw data from target: {current_url}")

        response = polite_get(current_url, public_headers)
        if response is None:
            logging.error("Page could not be fetched after retries. Ending pipeline.")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        books_html = soup.find_all("article", class_="product_pod")

        for book in books_html:
            if scraped_count >= TARGET_COUNT:
                break

            try:
                title = book.h3.a["title"] if book.h3 and book.h3.a else ""

                price_el = book.find("p", class_="price_color")
                raw_price = price_el.text if price_el else ""

                rating_el = book.find("p", class_="star-rating")
                raw_rating = rating_el["class"] if rating_el else []

                avail_el = book.find("p", class_="instock availability")
                raw_avail = avail_el.text if avail_el else ""

                book_data = {
                    "title": title,
                    "price": parse_price(raw_price),
                    "rating": parse_rating(raw_rating),
                    "availability": parse_availability(raw_avail),
                }

                validated_book = BookSchema(**book_data)

                # NOTE: your TaskBlueprint only has title/completed, so rating
                # still gets folded into the title string below — that's a
                # backend schema limit, not something this script can fix on
                # its own. If you want rating/price stored as real fields,
                # TaskBlueprint and the `items` table need new columns.
                api_payload = {
                    "title": f"{validated_book.title} (£{validated_book.price}, {validated_book.rating}★)",
                    "completed": validated_book.availability,
                }

                api_response = requests.post(
                    API_INGEST_URL, json=api_payload, headers=private_headers, timeout=5
                )

                if api_response.status_code == 200:
                    scraped_count += 1
                    logging.info(f"Success [{scraped_count}/{TARGET_COUNT}]: Safe insertion into database.")
                else:
                    logging.warning(
                        f"Backend API rejection on item. HTTP Code: {api_response.status_code} "
                        f"- Reason: {api_response.text}"
                    )

            except ValidationError as ve:
                logging.error(f"Input Validation Failed. Data dropped before API transmission. Error: {ve}")
            except Exception as e:
                logging.error(f"Incident isolated: Parsing error on individual book element. Error: {e}")

        next_button = soup.find("li", class_="next")
        if next_button and next_button.a:
            current_url = urljoin(current_url, next_button.a["href"])
        else:
            current_url = None

        time.sleep(REQUEST_DELAY)

    logging.info(f"Pipeline closed. Securely synchronized {scraped_count} clean records.")


if __name__ == "__main__":
    run_secure_pipeline()