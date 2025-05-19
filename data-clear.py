import sqlite3
import os

# Database file path - must match the path in main.py
DATABASE = '/nfs/app.db'

def get_db():
    """Connect to the database and return a connection object."""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row  # Enables name-based access to columns
    return db

def clear_data():
    """Clear all data from the contacts table."""
    if not os.path.exists(DATABASE):
        print(f"Database file {DATABASE} does not exist. Nothing to clear.")
        return
    
    db = get_db()
    
    # First, count how many contacts we have
    count = db.execute('SELECT COUNT(*) FROM contacts').fetchone()[0]
    print(f"Found {count} contacts in the database.")
    
    # Delete all contacts
    db.execute('DELETE FROM contacts')
    db.commit()
    
    # Verify deletion
    new_count = db.execute('SELECT COUNT(*) FROM contacts').fetchone()[0]
    print(f"After deletion, database contains {new_count} contacts.")
    
    print("All test data has been cleared.")

if __name__ == "__main__":
    print("Starting data cleanup...")
    clear_data()
    print("Data cleanup complete.")