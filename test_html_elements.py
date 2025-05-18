from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import unittest
import time

class TestContacts(unittest.TestCase):
    def setUp(self):
        # Setup Firefox options
        firefox_options = Options()
        firefox_options.add_argument("--headless")  # Ensures the browser window does not open
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Firefox(options=firefox_options)

    def test_contacts(self):
        driver = self.driver
        driver.get("http://10.48.10.170")  # PROD IP for testing
        
        # Wait for page to load
        time.sleep(2)
        
        # Check for the presence of all 10 test contacts
        for i in range(10):
            test_name = f'Test Name {i}'
            assert test_name in driver.page_source, f"Test contact {test_name} not found in page source"
        
        # Check for page elements
        assert "Contact Manager" in driver.page_source, "Page title not found"
        assert "Add New Contact" in driver.page_source, "Add form not found"
        
        print("Test completed successfully. All 10 test contacts were verified.")

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
