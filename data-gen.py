import sqlite3
import os
import random
import time

# Database file path - must match the path in main.py
DATABASE = '/nfs/app.db'

def get_db():
    """Connect to the database and return a connection object."""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row  # Enables name-based access to columns
    return db

def init_db():
    """Initialize the database schema if it doesn't exist."""
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL
        );
    ''')
    db.commit()
    print("Database initialized successfully.")

def generate_test_data(num_contacts=10):
    """Generate random test contacts."""
    db = get_db()
    
    # First, check if we already have data
    existing_count = db.execute('SELECT COUNT(*) FROM contacts').fetchone()[0]
    print(f"Found {existing_count} existing contacts in the database.")
    
    if existing_count > 0:
        print("Database already contains data. Skipping test data generation.")
        return
    
    # Generate random contacts
    for i in range(num_contacts):
        name = f"Test User {random.randint(1000, 9999)}"
        phone = f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        email = f"test{random.randint(1000, 9999)}@example.com"
        
        db.execute('INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)', 
                  (name, phone, email))
        print(f"Added contact: {name}, {phone}, {email}")
    
    db.commit()
    print(f"Successfully generated {num_contacts} test contacts.")

def verify_data():
    """Verify that data was added to the database."""
    db = get_db()
    contacts = db.execute('SELECT * FROM contacts').fetchall()
    
    print(f"Database contains {len(contacts)} contacts:")
    for contact in contacts[:5]:  # Print first 5 contacts
        print(f"  - {contact['name']}, {contact['phone']}, {contact['email']}")
    
    if len(contacts) > 5:
        print(f"  ... and {len(contacts) - 5} more")

def ensure_db_directory():
    """Ensure the directory for the database file exists."""
    db_dir = os.path.dirname(DATABASE)
    if not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir)
            print(f"Created directory: {db_dir}")
        except Exception as e:
            print(f"Error creating directory {db_dir}: {e}")
            # Try to continue anyway

def main():
    print("Starting test data generation...")
    print(f"Database path: {DATABASE}")
    
    # Ensure the database directory exists
    ensure_db_directory()
    
    # Wait a moment to ensure the Flask app has initialized the database
    time.sleep(2)
    
    # Initialize the database schema
    init_db()
    
    # Generate test data
    generate_test_data(10)
    
    # Verify the data was added
    verify_data()
    
    print("Test data generation complete.")

if __name__ == "__main__":
    main()