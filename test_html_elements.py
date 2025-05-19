import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
import os
import time
import socket
import urllib.request
import urllib.error
import random

class TestHtmlElements(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up the test class - runs once before all tests."""
        print("Setting up test class...")
        # Ensure we have a clean environment for testing
        try:
            # You could add code here to ensure the database is in a known state
            print("Test class setup complete")
        except Exception as e:
            print(f"Error in setUpClass: {e}")
    
    def setUp(self):
        # Set up headless Firefox browser
        options = Options()
        options.add_argument("--headless")
        
        # Add more Firefox options to improve stability
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        
        # Initialize the driver
        self.driver = webdriver.Firefox(options=options)
        self.driver.set_page_load_timeout(60)  # Increase page load timeout
        
        # Get the Flask app URL from environment variable or use the specified IP
        flask_url = os.environ.get('FLASK_URL', 'http://10.48.10.216:5000')
        print("Connecting to Flask app at:", flask_url)
        
        # Check if the service is reachable first
        self._check_service_availability(flask_url)
        
        # Try to resolve the hostname first if it's not an IP address
        if not self._is_ip_address(flask_url.split('//')[1].split(':')[0]):
            self._check_dns_resolution(flask_url)
        
        # Try to connect to the Flask app with retries
        max_retries = 15  # Increase retries further
        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt + 1}/{max_retries} to load page")
                self.driver.get(flask_url)
                print("Successfully connected to", flask_url)
                
                # Wait for the page to be fully loaded
                WebDriverWait(self.driver, 20).until(  # Increase wait time
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                print("Page fully loaded")
                break
            except (WebDriverException, TimeoutException) as e:
                if attempt < max_retries - 1:
                    print("Connection attempt", attempt + 1, "failed:", str(e))
                    print("Retrying in 15 seconds...")  # Increase wait time
                    time.sleep(15)
                else:
                    print("All", max_retries, "connection attempts failed")
                    raise e
    
    def _check_service_availability(self, url):
        """Check if the service is available using urllib."""
        print(f"Checking if {url} is available...")
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                with urllib.request.urlopen(url, timeout=10) as response:
                    if response.status == 200:
                        print(f"Service at {url} is available (Status: {response.status})")
                        return True
                    print(f"Service returned status code: {response.status}")
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
                print(f"Request attempt {attempt + 1} failed: {e}")
                if attempt < max_attempts - 1:
                    print("Retrying in 5 seconds...")
                    time.sleep(5)
        
        print(f"Warning: Service at {url} may not be available")
        return False
    
    def _is_ip_address(self, host):
        """Check if the host is an IP address."""
        try:
            socket.inet_aton(host)
            return True
        except socket.error:
            return False
    
    def _check_dns_resolution(self, url):
        """Check if the hostname in the URL can be resolved."""
        hostname = url.split('//')[1].split(':')[0]
        try:
            print("Resolving hostname:", hostname)
            ip = socket.gethostbyname(hostname)
            print("Hostname", hostname, "resolved to", ip)
        except socket.gaierror as e:
            print("DNS resolution failed for", hostname, ":", str(e))
            print("Attempting to use /etc/hosts or equivalent...")
    
    def _add_test_contact(self):
        """Helper method to add a test contact and return its details."""
        try:
            # Generate a unique test contact
            test_name = f"Test User {random.randint(1000, 9999)}"
            test_phone = f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            test_email = f"test{random.randint(1000, 9999)}@example.com"
            
            # Find form elements
            name_input = self.driver.find_element(By.NAME, "name")
            phone_input = self.driver.find_element(By.NAME, "phone")
            email_input = self.driver.find_element(By.NAME, "email")
            submit_button = self.driver.find_element(By.XPATH, "//input[@type='submit']")
            
            # Fill out the form
            print(f"Adding contact: {test_name}, {test_phone}, {test_email}")
            name_input.clear()  # Clear any existing text
            name_input.send_keys(test_name)
            phone_input.clear()
            phone_input.send_keys(test_phone)
            email_input.clear()
            email_input.send_keys(test_email)
            
            # Submit the form
            submit_button.click()
            
            # Wait for page to reload
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            
            # Verify the contact was added
            page_source = self.driver.page_source
            self.assertIn(test_name, page_source, f"Added contact {test_name} not found in page")
            
            print(f"Successfully added contact: {test_name}")
            return test_name, test_phone, test_email
            
        except (TimeoutException, NoSuchElementException, AssertionError) as e:
            print("Error in _add_test_contact:", str(e))
            # Take screenshot for debugging
            self.driver.save_screenshot('add_contact_error.png')
            raise
    
    def test_1_page_title(self):
        # Check if the page title is correct
        try:
            print("Page title:", self.driver.title)
            self.assertEqual("Contact Manager", self.driver.title)
        except AssertionError as e:
            print("Error in test_page_title:", str(e))
            # Take screenshot for debugging
            self.driver.save_screenshot('title_test_error.png')
            raise
    
    def test_2_form_exists(self):
        try:
            # Wait for form to be present
            form = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )
            self.assertIsNotNone(form)
            
            # Wait for inputs to be present
            name_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "name"))
            )
            phone_input = self.driver.find_element(By.NAME, "phone")
            email_input = self.driver.find_element(By.NAME, "email")
            
            self.assertIsNotNone(name_input)
            self.assertIsNotNone(phone_input)
            self.assertIsNotNone(email_input)
            
            # Check if the form is visible and interactive
            self.assertTrue(name_input.is_displayed(), "Name input is not displayed")
            self.assertTrue(name_input.is_enabled(), "Name input is not enabled")
            
        except (TimeoutException, NoSuchElementException, AssertionError) as e:
            print("Error in test_form_exists:", str(e))
            # Take screenshot for debugging
            self.driver.save_screenshot('form_test_error.png')
            raise
    
    def test_3_add_contact(self):
        try:
            self._add_test_contact()
        except Exception as e:
            print("Error in test_add_contact:", str(e))
            # Take screenshot for debugging
            self.driver.save_screenshot('add_contact_error.png')
            raise
    
    def test_4_table_exists(self):
        try:
            # Wait for table to be present
            table = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            self.assertIsNotNone(table)
            
            # Wait for headers to be present
            headers = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "th"))
            )
            self.assertEqual(len(headers), 5)  # ID, Name, Phone, Email, Action
        except (TimeoutException, NoSuchElementException, AssertionError) as e:
            print("Error in test_table_exists:", str(e))
            # Take screenshot for debugging
            self.driver.save_screenshot('table_test_error.png')
            raise
    
    def test_5_edit_contact(self):
        try:
            # First, add a contact to edit
            test_name, test_phone, test_email = self._add_test_contact()
            
            # Find and click the edit button for the contact we just added
            edit_button = self.driver.find_element(By.XPATH, f"//td[contains(text(), '{test_name}')]/following-sibling::td//a[contains(@class, 'edit-btn')]")
            edit_button.click()
            
            # Wait for the edit modal to appear
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "editModal"))
            )
            
            # Generate new data for the edit
            edited_name = f"Edited {test_name}"
            edited_phone = f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            edited_email = f"edited{random.randint(1000, 9999)}@example.com"
            
            # Find the edit form elements
            edit_name_input = self.driver.find_element(By.ID, "editName")
            edit_phone_input = self.driver.find_element(By.ID, "editPhone")
            edit_email_input = self.driver.find_element(By.ID, "editEmail")
            edit_submit_button = self.driver.find_element(By.XPATH, "//form[@id='editForm']//input[@type='submit']")
            
            # Clear existing values and enter new values
            edit_name_input.clear()
            edit_name_input.send_keys(edited_name)
            edit_phone_input.clear()
            edit_phone_input.send_keys(edited_phone)
            edit_email_input.clear()
            edit_email_input.send_keys(edited_email)
            
            # Submit the edit form
            print(f"Editing contact to: {edited_name}, {edited_phone}, {edited_email}")
            edit_submit_button.click()
            
            # Wait for page to reload
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            
            # Verify the contact was edited
            updated_page_source = self.driver.page_source
            self.assertIn(edited_name, updated_page_source, f"Edited contact name {edited_name} not found in page")
            self.assertIn(edited_phone, updated_page_source, f"Edited contact phone {edited_phone} not found in page")
            self.assertIn(edited_email, updated_page_source, f"Edited contact email {edited_email} not found in page")
            
            print(f"Successfully edited and verified contact: {edited_name}")
            
        except (TimeoutException, NoSuchElementException, AssertionError) as e:
            print("Error in test_edit_contact:", str(e))
            # Take screenshot for debugging
            self.driver.save_screenshot('edit_contact_error.png')
            raise
    
    def test_6_contacts_exist(self):
        try:
            # Wait for table to be present
            table = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            
            # Print page source for debugging
            print("Page source excerpt:")
            print(self.driver.page_source[:500] + "...")
            
            # Check for contacts in the table
            rows = self.driver.find_elements(By.TAG_NAME, "tr")
            print(f"Found {len(rows)} rows in the table")
            
            # Skip header row
            data_rows = rows[1:] if len(rows) > 0 else []
            print(f"Found {len(data_rows)} data rows")
            
            # Check if we have at least one contact
            self.assertGreater(len(data_rows), 0, "No contacts found in the table")
            
            # Print the first few contacts for debugging
            for i, row in enumerate(data_rows[:3]):
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 2:  # At least ID and Name
                    print(f"Contact {i+1}: {cells[1].text}")
            
        except (TimeoutException, NoSuchElementException, AssertionError) as e:
            print("Error in test_contacts_exist:", str(e))
            # Take screenshot for debugging
            self.driver.save_screenshot('contacts_test_error.png')
            raise
    
    def tearDown(self):
        if hasattr(self, 'driver'):
            try:
                self.driver.quit()
            except WebDriverException as e:
                print("Error in tearDown:", str(e))
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests have run."""
        print("Cleaning up after tests...")
        # You could add code here to clean up the database if needed
        print("Test class cleanup complete")

if __name__ == "__main__":
    unittest.main()
