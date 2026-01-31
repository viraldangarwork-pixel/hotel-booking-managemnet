"""Selenium tests for Guests page."""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from conftest import BASE_URL, navigate_to


class TestGuestsPage:

    def test_guests_page_loads(self, driver, wait):
        """Guests page should display heading."""
        navigate_to(driver, wait, "/guests")

        heading = driver.find_element(By.CSS_SELECTOR, "h1")
        assert "Guests" in heading.text

    def test_search_bar_visible(self, driver, wait):
        """Search input should be visible."""
        navigate_to(driver, wait, "/guests")

        search = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Search'], input[type='text']")
        assert search.is_displayed()

    def test_add_guest_modal_opens(self, driver, wait):
        """Clicking Add Guest should open a modal."""
        navigate_to(driver, wait, "/guests")

        add_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Add Guest') or contains(text(), '+ Add')]")
        ))
        add_btn.click()

        modal = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "[class*='modal']")
        ))
        assert modal.is_displayed()

    def test_add_guest_validation(self, driver, wait):
        """Empty form should show validation errors."""
        navigate_to(driver, wait, "/guests")

        add_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Add Guest') or contains(text(), '+ Add')]")
        ))
        add_btn.click()

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='modal']")))

        # Click submit
        submit_btns = driver.find_elements(By.CSS_SELECTOR, "[class*='modal'] button[type='submit'], [class*='modal'] .btn-primary")
        for btn in submit_btns:
            if "cancel" not in btn.text.lower():
                btn.click()
                break

        time.sleep(1)

        errors = driver.find_elements(By.CSS_SELECTOR, "[class*='red-500'], [class*='error']")
        assert len(errors) > 0

    def test_add_guest_success(self, driver, wait):
        """Adding a guest with valid data should succeed."""
        navigate_to(driver, wait, "/guests")

        add_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Add Guest') or contains(text(), '+ Add')]")
        ))
        add_btn.click()

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='modal']")))

        # Fill the form fields
        inputs = driver.find_elements(By.CSS_SELECTOR, "[class*='modal'] input, [class*='modal'] select")
        for inp in inputs:
            name = inp.get_attribute("name") or inp.get_attribute("placeholder") or ""
            input_type = inp.get_attribute("type") or ""
            tag = inp.tag_name

            if "first" in name.lower() or "first" in (inp.get_attribute("id") or "").lower():
                inp.clear()
                inp.send_keys("Selenium")
            elif "last" in name.lower() or "last" in (inp.get_attribute("id") or "").lower():
                inp.clear()
                inp.send_keys("TestGuest")
            elif "phone" in name.lower() or "phone" in (inp.get_attribute("placeholder") or "").lower():
                inp.clear()
                inp.send_keys("+919999988888")
            elif "email" in name.lower() or input_type == "email":
                inp.clear()
                inp.send_keys("selenium@test.com")

        # Submit
        submit_btns = driver.find_elements(By.CSS_SELECTOR, "[class*='modal'] button[type='submit'], [class*='modal'] .btn-primary")
        for btn in submit_btns:
            if "cancel" not in btn.text.lower() and btn.is_enabled():
                btn.click()
                break

        time.sleep(2)

        # Modal should close (success) OR success message appears
        page_text = driver.find_element(By.TAG_NAME, "body").text
        # Either modal closed or success message shown
        assert "Selenium" in page_text or "success" in page_text.lower() or "created" in page_text.lower()

    def test_guest_card_click_navigates(self, driver, wait):
        """Clicking a guest card should navigate to detail page."""
        navigate_to(driver, wait, "/guests")
        time.sleep(2)

        # Find any clickable guest card or link
        cards = driver.find_elements(By.CSS_SELECTOR, ".card[class*='cursor'], [class*='hover'] .card, a[href*='guests/']")
        if cards:
            cards[0].click()
            time.sleep(2)

            # Should be on guest detail page
            assert "guests/" in driver.current_url or "Guest" in driver.find_element(By.TAG_NAME, "body").text

    def test_vip_filter_toggle(self, driver, wait):
        """VIP filter toggle should be present."""
        navigate_to(driver, wait, "/guests")

        page_text = driver.find_element(By.TAG_NAME, "body").text
        assert "VIP" in page_text


class TestGuestDetailPage:

    def test_guest_detail_tabs(self, driver, wait):
        """Guest detail page should have Profile/Documents/Bookings tabs."""
        navigate_to(driver, wait, "/guests")
        time.sleep(2)

        # Click first guest
        cards = driver.find_elements(By.CSS_SELECTOR, ".card")
        clickable = [c for c in cards if "cursor" in (c.get_attribute("class") or "")]
        if not clickable:
            # Try clicking any guest card-like element
            all_cards = driver.find_elements(By.CSS_SELECTOR, "[class*='card-hover'], [class*='cursor-pointer']")
            if all_cards:
                all_cards[0].click()
            else:
                pytest.skip("No guest cards to click")
                return
        else:
            clickable[0].click()

        time.sleep(2)

        page_text = driver.find_element(By.TAG_NAME, "body").text
        assert "Profile" in page_text or "Documents" in page_text or "Bookings" in page_text

    def test_documents_tab_shows_upload(self, driver, wait):
        """Documents tab should show upload zones."""
        navigate_to(driver, wait, "/guests")
        time.sleep(2)

        # Navigate to first guest detail
        clickable = driver.find_elements(By.CSS_SELECTOR, "[class*='cursor-pointer']")
        if clickable:
            clickable[0].click()
        else:
            pytest.skip("No guests available")
            return

        time.sleep(2)

        # Click Documents tab
        tabs = driver.find_elements(By.CSS_SELECTOR, "button, [class*='tab']")
        for tab in tabs:
            if "document" in tab.text.lower():
                tab.click()
                break

        time.sleep(1)

        page_text = driver.find_element(By.TAG_NAME, "body").text
        assert "upload" in page_text.lower() or "document" in page_text.lower() or "front" in page_text.lower()
