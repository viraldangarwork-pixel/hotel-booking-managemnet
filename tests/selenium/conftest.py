"""Selenium test configuration and shared fixtures."""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ============================================
# CONFIGURATION — Change these to match your setup
# ============================================
BASE_URL = "http://localhost:5173"
ADMIN_EMAIL = "admin@hotel.com"
ADMIN_PASSWORD = "Admin@123"
WAIT_TIMEOUT = 10  # seconds
# ============================================


@pytest.fixture(scope="session")
def driver():
    """Create a Chrome WebDriver that persists across the session."""
    options = Options()
    # options.add_argument("--headless")  # Uncomment to run headless
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=options)
    browser.implicitly_wait(5)

    yield browser

    browser.quit()


@pytest.fixture(scope="session")
def wait(driver):
    """WebDriverWait instance."""
    return WebDriverWait(driver, WAIT_TIMEOUT)


@pytest.fixture(scope="session", autouse=True)
def login(driver, wait):
    """Login once at the start of the test session."""
    driver.get(f"{BASE_URL}/login")

    # Wait for login page to load
    wait.until(EC.presence_of_element_located((By.ID, "email")))

    email_input = driver.find_element(By.ID, "email")
    password_input = driver.find_element(By.ID, "password")

    email_input.clear()
    email_input.send_keys(ADMIN_EMAIL)
    password_input.clear()
    password_input.send_keys(ADMIN_PASSWORD)

    # Click submit
    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_btn.click()

    # Wait for redirect to dashboard (URL should not contain /login)
    wait.until(lambda d: "/login" not in d.current_url)

    # Wait for sidebar to appear (confirms dashboard loaded)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "nav, aside, [class*='sidebar']")))


def navigate_to(driver, wait, path):
    """Navigate to a page and wait for it to load."""
    driver.get(f"{BASE_URL}{path}")
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1")))


def click_sidebar_link(driver, wait, text):
    """Click a sidebar navigation link by its text content."""
    links = driver.find_elements(By.CSS_SELECTOR, "nav a, aside a")
    for link in links:
        if text.lower() in link.text.lower():
            link.click()
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1")))
            return
    raise Exception(f"Sidebar link '{text}' not found")
