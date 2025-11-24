# selenium_service.py
from typing import Dict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def get_page_title(url: str) -> Dict[str, str]:
    """
    Launch a headless browser, open the URL, and return basic info.
    """
    options = Options()
    # Selenium 4 / recent Chrome prefers this form for headless mode. :contentReference[oaicite:3]{index=3}
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        title = driver.title
        return {"url": url, "title": title}
    finally:
        driver.quit()
