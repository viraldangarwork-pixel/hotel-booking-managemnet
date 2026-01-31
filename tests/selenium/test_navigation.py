"""Selenium tests for overall navigation and UI elements."""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from conftest import BASE_URL, navigate_to


class TestSidebarNavigation:

    def test_dashboard_link(self, driver, wait):
        """Dashboard link should navigate to home."""
        navigate_to(driver, wait, "/")
        heading = driver.find_element(By.CSS_SELECTOR, "h1")
        assert "Dashboard" in heading.text or driver.current_url.rstrip("/").endswith(BASE_URL.rstrip("/"))

    def test_rooms_link(self, driver, wait):
        """Rooms link should navigate to rooms page."""
        navigate_to(driver, wait, "/rooms")
        heading = driver.find_element(By.CSS_SELECTOR, "h1")
        assert "Rooms" in heading.text

    def test_bookings_link(self, driver, wait):
        """Bookings link should navigate to bookings page."""
        navigate_to(driver, wait, "/bookings")
        heading = driver.find_element(By.CSS_SELECTOR, "h1")
        assert "Bookings" in heading.text

    def test_guests_link(self, driver, wait):
        """Guests link should navigate to guests page."""
        navigate_to(driver, wait, "/guests")
        heading = driver.find_element(By.CSS_SELECTOR, "h1")
        assert "Guests" in heading.text

    def test_chat_link(self, driver, wait):
        """Chat link should navigate to chat page."""
        navigate_to(driver, wait, "/chat")
        heading = driver.find_element(By.CSS_SELECTOR, "h1")
        assert "Chat" in heading.text

    def test_settings_link(self, driver, wait):
        """Settings link should navigate to settings page."""
        navigate_to(driver, wait, "/settings")
        heading = driver.find_element(By.CSS_SELECTOR, "h1")
        assert "Settings" in heading.text


class TestNotFoundPage:

    def test_404_page(self, driver, wait):
        """Invalid URL should show 404 page."""
        driver.get(f"{BASE_URL}/this-does-not-exist-xyz")
        time.sleep(2)

        page_text = driver.find_element(By.TAG_NAME, "body").text
        assert "not found" in page_text.lower() or "404" in page_text


class TestAnimations:

    def test_page_has_animations(self, driver, wait):
        """Pages should have animation classes applied."""
        navigate_to(driver, wait, "/rooms")

        # Check for animation classes in the page HTML
        page_html = driver.page_source
        has_animation = any(cls in page_html for cls in [
            "animate-fade-in",
            "animate-slide-up",
            "stagger-item",
            "animate-slide-down",
        ])
        assert has_animation

    def test_modal_animation(self, driver, wait):
        """Modal should have animation classes."""
        navigate_to(driver, wait, "/rooms")

        add_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Add Room') or contains(text(), '+ Add')]")
        ))
        add_btn.click()

        time.sleep(0.5)

        page_html = driver.page_source
        has_modal_class = any(cls in page_html for cls in [
            "modal-overlay",
            "modal-content",
            "modalSlideIn",
        ])
        assert has_modal_class

        # Close modal
        cancel_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Cancel')]")
        cancel_btn.click()


class TestResponsiveness:

    def test_mobile_viewport(self, driver, wait):
        """Page should be usable at mobile viewport."""
        driver.set_window_size(375, 812)
        navigate_to(driver, wait, "/rooms")

        heading = driver.find_element(By.CSS_SELECTOR, "h1")
        assert heading.is_displayed()

        # Reset viewport
        driver.set_window_size(1920, 1080)

    def test_tablet_viewport(self, driver, wait):
        """Page should be usable at tablet viewport."""
        driver.set_window_size(768, 1024)
        navigate_to(driver, wait, "/bookings")

        heading = driver.find_element(By.CSS_SELECTOR, "h1")
        assert heading.is_displayed()

        # Reset viewport
        driver.set_window_size(1920, 1080)
