import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
import time
import os
import socket
import random

class TestContacts(unittest.TestCase):
    def setUp(self):
        # Setup Firefox options
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Firefox(options=firefox_options)
        self.driver.implicitly_wait(10)
        self.driver.set_page_load_timeout(60)
        
        # Use the correct IP address for the Flask app
        self.flask_url = os.environ.get('FLASK_URL', 'http://10.48.10.216')
        print(f"Using Flask URL: {self.flask_url}")

    def test_contacts(self):
        driver = self.driver
        try:
            # Navigate to the application
            print(f"Navigating to {self.flask_url}...")
            driver.get(self.flask_url)
            
            # Print page title and URL for debugging
            print(f"Page title: {driver.title}")
            print(f"Current URL: {driver.current_url}")
            
            # Wait for page to load
            print("Waiting for page to load...")
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Add a test contact using the form
            print("Adding test contact...")
            
            # Generate a unique test name to verify it was added
            test_name = f"Test Name {random.randint(1000, 9999)}"
            test_phone = f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            test_email = f"test{random.randint(1000, 9999)}@example.com"
            
            # Find form elements
            name_input = driver.find_element(By.NAME, "name")
            phone_input = driver.find_element(By.NAME, "phone")
            email_input = driver.find_element(By.NAME, "email")
            submit_button = driver.find_element(By.XPATH, "//input[@type='submit']")
            
            # Fill out the form
            name_input.send_keys(test_name)
            phone_input.send_keys(test_phone)
            email_input.send_keys(test_email)
            
            # Submit the form
            print(f"Submitting form with name: {test_name}, phone: {test_phone}, email: {test_email}")
            submit_button.click()
            
            # Wait for page to reload after submission
            print("Waiting for page to reload after form submission...")
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            
            # Print page source excerpt for debugging
            print("Page source excerpt after adding contact:")
            print(driver.page_source[:500] + "...")
            
            # Verify the contact was added
            print("Verifying contact was added...")
            self.assertIn(test_name, driver.page_source, f"Test contact {test_name} not found in page source")
            
            # Check for table presence
            print("Checking for table...")
            table = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            print("Table found")
            
            # Get all rows
            rows = driver.find_elements(By.TAG_NAME, "tr")
            print(f"Found {len(rows)} rows in the table")
            
            # Skip header row
            data_rows = rows[1:] if len(rows) > 0 else []
            print(f"Found {len(data_rows)} data rows")
            
            # Print the first few contacts for debugging
            for i, row in enumerate(data_rows[:3]):
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 2:  # At least ID and Name
                    print(f"Contact {i+1}: {cells[1].text}")
            
            # Check if we have at least one contact
            self.assertGreater(len(data_rows), 0, "No contacts found in the table")
            
        except Exception as e:
            print(f"Test failed with exception: {str(e)}")
            driver.save_screenshot('test_error.png')
            raise

    def tearDown(self):
        if hasattr(self, 'driver'):
            self.driver.quit()

if __name__ == "__main__":
    unittest.main()
