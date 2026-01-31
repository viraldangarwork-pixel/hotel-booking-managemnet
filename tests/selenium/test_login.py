"""Selenium tests for Login page."""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from conftest import BASE_URL, ADMIN_EMAIL, ADMIN_PASSWORD


class TestLoginPage:

    def test_page_loads(self, driver, wait):
        """Login page should show title and form."""
        driver.get(f"{BASE_URL}/login")
        wait.until(EC.presence_of_element_located((By.ID, "email")))

        heading = driver.find_element(By.CSS_SELECTOR, "h1")
        assert "Hotel Management" in heading.text

        assert driver.find_element(By.ID, "email").is_displayed()
        assert driver.find_element(By.ID, "password").is_displayed()
        assert driver.find_element(By.CSS_SELECTOR, "button[type='submit']").is_displayed()

    def test_login_with_wrong_password(self, driver, wait):
        """Wrong password should show error message."""
        driver.get(f"{BASE_URL}/login")
        wait.until(EC.presence_of_element_located((By.ID, "email")))

        driver.find_element(By.ID, "email").clear()
        driver.find_element(By.ID, "email").send_keys(ADMIN_EMAIL)
        driver.find_element(By.ID, "password").clear()
        driver.find_element(By.ID, "password").send_keys("WrongPassword123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Error message should appear
        error = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "[class*='red'], [class*='error']")
        ))
        assert error.is_displayed()

    def test_login_success_redirects(self, driver, wait):
        """Correct credentials should redirect to dashboard."""
        driver.get(f"{BASE_URL}/login")
        wait.until(EC.presence_of_element_located((By.ID, "email")))

        driver.find_element(By.ID, "email").clear()
        driver.find_element(By.ID, "email").send_keys(ADMIN_EMAIL)
        driver.find_element(By.ID, "password").clear()
        driver.find_element(By.ID, "password").send_keys(ADMIN_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        wait.until(lambda d: "/login" not in d.current_url)
        assert "/login" not in driver.current_url

    def test_protected_route_redirects_to_login(self, driver, wait):
        """Accessing protected route without auth should redirect to login."""
        # Clear localStorage to simulate logged out
        driver.execute_script("localStorage.clear()")
        driver.get(f"{BASE_URL}/rooms")

        wait.until(EC.url_contains("/login"))
        assert "/login" in driver.current_url

        # Log back in for other tests
        driver.find_element(By.ID, "email").clear()
        driver.find_element(By.ID, "email").send_keys(ADMIN_EMAIL)
        driver.find_element(By.ID, "password").clear()
        driver.find_element(By.ID, "password").send_keys(ADMIN_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(lambda d: "/login" not in d.current_url)
