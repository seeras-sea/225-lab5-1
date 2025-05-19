from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import unittest

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
        driver.get("http://10.48.10.216/")  # Replace with your target website
        
        # Check for the presence of test contacts
        assert "Test User" in driver.page_source, "No test contacts found in page source"
        
        # Check that we have a table with contacts
        assert "<table>" in driver.page_source, "No contact table found in page source"
        
        # Check that we have the Contact Manager title
        assert "Contact Manager" in driver.page_source, "Contact Manager title not found"
        
        print("Test completed successfully. Test contacts were verified.")

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
