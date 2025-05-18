import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

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
        
        # Get the Flask app URL from environment variable or use the specified IP
        self.flask_url = os.environ.get('FLASK_URL', 'http://10.48.10.170:5000')
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
            
            # Print page source excerpt for debugging
            print("Page source excerpt:")
            print(driver.page_source[:500] + "...")
            
            # Check for table presence
            print("Checking for table...")
            try:
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
                print(f"Error finding table: {str(e)}")
                
                # Check if we're on the right page
                if "Contact Manager" in driver.title:
                    print("On correct page, but table not found")
                else:
                    print(f"Wrong page: {driver.title}")
                
                # Take screenshot for debugging
                driver.save_screenshot('table_error.png')
                raise
            
        except Exception as e:
            print(f"Test failed with exception: {str(e)}")
            driver.save_screenshot('test_error.png')
            raise

    def tearDown(self):
        if hasattr(self, 'driver'):
            self.driver.quit()

if __name__ == "__main__":
    unittest.main()
