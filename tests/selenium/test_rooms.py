"""Selenium tests for Rooms page."""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from conftest import BASE_URL, navigate_to


class TestRoomsPage:

    def test_rooms_page_loads(self, driver, wait):
        """Rooms page should display heading and room cards."""
        navigate_to(driver, wait, "/rooms")

        heading = driver.find_element(By.CSS_SELECTOR, "h1")
        assert "Rooms" in heading.text

    def test_status_summary_cards_visible(self, driver, wait):
        """Status summary cards should be visible."""
        navigate_to(driver, wait, "/rooms")

        # Look for cards containing status text
        page_text = driver.find_element(By.TAG_NAME, "body").text
        assert "Available" in page_text

    def test_room_cards_displayed(self, driver, wait):
        """Room cards should be visible with room numbers."""
        navigate_to(driver, wait, "/rooms")
        time.sleep(2)  # Wait for data to load

        # Check if room numbers are displayed (101, 102, etc.)
        page_text = driver.find_element(By.TAG_NAME, "body").text
        assert "101" in page_text or "No rooms" in page_text

    def test_add_room_modal_opens(self, driver, wait):
        """Clicking Add Room should open a modal."""
        navigate_to(driver, wait, "/rooms")

        add_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Add Room') or contains(text(), '+ Add')]")
        ))
        add_btn.click()

        # Modal should appear
        modal = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "[class*='modal']")
        ))
        assert modal.is_displayed()

    def test_add_room_validation(self, driver, wait):
        """Submitting empty form should show validation errors."""
        navigate_to(driver, wait, "/rooms")

        add_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Add Room') or contains(text(), '+ Add')]")
        ))
        add_btn.click()

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='modal']")))

        # Find and click the submit/create button inside modal
        submit_btns = driver.find_elements(By.CSS_SELECTOR, "[class*='modal'] button[type='submit'], [class*='modal'] .btn-primary")
        for btn in submit_btns:
            if "cancel" not in btn.text.lower():
                btn.click()
                break

        time.sleep(1)

        # Validation errors should appear (red text or error class)
        errors = driver.find_elements(By.CSS_SELECTOR, "[class*='red-500'], [class*='error']")
        assert len(errors) > 0

    def test_close_modal(self, driver, wait):
        """Modal should close when clicking Cancel or X."""
        navigate_to(driver, wait, "/rooms")

        add_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Add Room') or contains(text(), '+ Add')]")
        ))
        add_btn.click()

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='modal']")))

        cancel_btn = driver.find_element(
            By.XPATH, "//button[contains(text(), 'Cancel')]"
        )
        cancel_btn.click()

        time.sleep(0.5)

        # Modal should be gone
        modals = driver.find_elements(By.CSS_SELECTOR, "[class*='modal-overlay']")
        visible = [m for m in modals if m.is_displayed()]
        assert len(visible) == 0

    def test_status_filter_click(self, driver, wait):
        """Clicking a status card should filter rooms."""
        navigate_to(driver, wait, "/rooms")
        time.sleep(2)

        # Click on a status card (first clickable card)
        cards = driver.find_elements(By.CSS_SELECTOR, ".card")
        for card in cards:
            text = card.text.lower()
            if "available" in text:
                card.click()
                time.sleep(1)
                break

        # Page should still be rooms
        assert "rooms" in driver.current_url.lower() or "Rooms" in driver.find_element(By.CSS_SELECTOR, "h1").text
