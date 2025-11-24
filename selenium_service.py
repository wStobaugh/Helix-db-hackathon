from __future__ import annotations
from typing import Dict, Any
import time
import os

# -------------------------
# 🚫 REMOVED the early __main__ block
# -------------------------

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def _new_driver(headless: bool = True) -> webdriver.Chrome:
    options = Options()
    if headless:
        # Headless mode for recent Chrome versions
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def get_page_title(url: str) -> Dict[str, str]:
    """
    Launch a headless browser, open the URL, and return basic info.
    """
    driver = _new_driver(headless=True)
    try:
        driver.get(url)
        title = driver.title
        return {"url": url, "title": title}
    finally:
        driver.quit()


def _login_with_cookie(driver: webdriver.Chrome, li_at: str) -> None:
    """Authenticate to LinkedIn using an existing li_at session cookie."""
    driver.get("https://www.linkedin.com/")
    driver.add_cookie({
        "name": "li_at",
        "value": li_at,
        "domain": ".www.linkedin.com",
        "path": "/",
        "secure": True,
        "httpOnly": True,
    })
    driver.get("https://www.linkedin.com/feed/")
    WebDriverWait(driver, 10).until(EC.title_contains("LinkedIn"))


def _login_with_credentials(driver: webdriver.Chrome, username: str, password: str) -> None:
    driver.get("https://www.linkedin.com/login")
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "username")))
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
    WebDriverWait(driver, 15).until(EC.any_of(
        EC.url_contains("/feed"),
        EC.title_contains("LinkedIn")
    ))


def _text_or_none(driver: webdriver.Chrome, by: By, selector: str) -> str | None:
    try:
        el = driver.find_element(by, selector)
        txt = el.text.strip()
        return txt if txt else None
    except Exception:
        return None


def _collect_experience(driver: webdriver.Chrome) -> list[Dict[str, Any]]:
    items: list[Dict[str, Any]] = []
    try:
        section = driver.find_element(By.CSS_SELECTOR, "section[id^=experience], section[data-view-name*=experience]")
        roles = section.find_elements(By.CSS_SELECTOR, "li")
        for li in roles[:10]:
            try:
                role = li.find_element(By.CSS_SELECTOR, "span[aria-hidden=true]").text.strip()
            except Exception:
                role = None
            try:
                company = li.find_element(By.CSS_SELECTOR, "span.t-14.t-normal").text.strip()
            except Exception:
                company = None
            try:
                dates = li.find_element(By.CSS_SELECTOR, "span.t-14.t-normal.t-black--light").text.strip()
            except Exception:
                dates = None
            if role or company or dates:
                items.append({"role": role, "company": company, "dates": dates})
    except Exception:
        pass
    return items


def scrape_linkedin_profile(url: str, auth: Dict[str, Any] | None = None, headless: bool = True) -> Dict[str, Any]:
    """
    Scrape basic LinkedIn profile data.
    """
    auth = auth or {}
    driver = _new_driver(headless=headless)
    try:
        method = (auth.get("method") or "cookie").lower()

        if method == "cookie" and auth.get("li_at"):
            _login_with_cookie(driver, auth["li_at"])
        elif method == "credentials" and auth.get("username") and auth.get("password"):
            _login_with_credentials(driver, auth["username"], auth["password"])
        else:
            driver.get("https://www.linkedin.com/")

        driver.get(url)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        time.sleep(1.5)

        name = (
            _text_or_none(driver, By.CSS_SELECTOR, "h1")
            or _text_or_none(driver, By.CSS_SELECTOR, ".pv-text-details__left-panel h1")
        )
        headline = (
            _text_or_none(driver, By.CSS_SELECTOR, "div.text-body-medium.break-words")
            or _text_or_none(driver, By.CSS_SELECTOR, "div.text-body-medium")
        )
        location = _text_or_none(driver, By.CSS_SELECTOR, "span.text-body-small.t-black--light")
        about = _text_or_none(driver, By.CSS_SELECTOR, "section[id^=about] div.inline-show-more-text")

        experiences = _collect_experience(driver)

        print(driver.find_element(By.TAG_NAME, "body").text)

        return {
            "url": url,
            "name": name,
            "headline": headline,
            "location": location,
            "about": about,
            "experiences": experiences,
            "authenticated": method in ("cookie", "credentials") and bool(auth),
        }
    finally:
        driver.quit()


# ----------------------------------------------------------
# ✅ CORRECT MAIN BLOCK — now at the bottom, works properly
# ----------------------------------------------------------
if __name__ == "__main__":
    profile_url = "https://www.linkedin.com/in/william-s-173477224/"

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    linkedin_cookie = os.getenv("LINKEDIN_COOKIE")
    linkedin_username = os.getenv("LINKEDIN_USERNAME")
    linkedin_password = os.getenv("LINKEDIN_PASSWORD")

    auth = None
    if linkedin_cookie:
        print("🔐 Using cookie-based authentication...")
        auth = {"method": "cookie", "li_at": linkedin_cookie}
    elif linkedin_username and linkedin_password:
        print("🔐 Using credentials-based authentication...")
        auth = {"method": "credentials", "username": linkedin_username, "password": linkedin_password}
    else:
        print("⚠️ No authentication provided – limited data will be available")

    print(f"\n🌐 Scraping profile: {profile_url}\n")

    result = scrape_linkedin_profile(profile_url, auth=auth, headless=False)

    print("\n" + "=" * 60)
    print("📊 SCRAPING RESULTS")
    print("=" * 60)
    print(result)
