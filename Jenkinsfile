from flask import Flask, request, render_template_string, redirect
import sqlite3

app = Flask(__name__)

# Database file path
DATABASE = '/nfs/app.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row  # Enables name-based access to columns
    return db

def init_db():
    with app.app_context():
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

@app.route('/')
def index():
    db = get_db()
    contacts = db.execute('SELECT * FROM contacts').fetchall()
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Contact Manager</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
            h1 { color: #333; }
            .container { max-width: 800px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #f2f2f2; }
            form { margin-top: 20px; }
            input[type="text"], input[type="email"] { padding: 8px; width: 100%; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 3px; }
            input[type="submit"] { padding: 8px 15px; background-color: #4CAF50; color: white; border: none; border-radius: 3px; cursor: pointer; }
            input[type="submit"]:hover { background-color: #45a049; }
            .delete-btn { padding: 5px 10px; background-color: #f44336; color: white; border: none; border-radius: 3px; cursor: pointer; }
            .delete-btn:hover { background-color: #d32f2f; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Contact Manager</h1>
            
            <form action="/add" method="post">
                <h3>Add New Contact</h3>
                <input type="text" name="name" placeholder="Name" required>
                <input type="text" name="phone" placeholder="Phone" required>
                <input type="email" name="email" placeholder="Email" required>
                <input type="submit" value="Add Contact">
            </form>
            
            <h3>Contacts</h3>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Phone</th>
                    <th>Email</th>
                    <th>Action</th>
                </tr>
                {% for contact in contacts %}
                <tr>
                    <td>{{ contact['id'] }}</td>
                    <td>{{ contact['name'] }}</td>
                    <td>{{ contact['phone'] }}</td>
                    <td>{{ contact['email'] }}</td>
                    <td>
                        <form action="/delete/{{ contact['id'] }}" method="post">
                            <button type="submit" class="delete-btn">Delete</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(html, contacts=contacts)

@app.route('/add', methods=['POST'])
def add_contact():
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    
    db = get_db()
    db.execute('INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)', 
               (name, phone, email))
    db.commit()
    
    return redirect('/')

@app.route('/delete/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    db = get_db()
    db.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
    db.commit()
    
    return redirect('/')

if __name__ == '__main__':
    # Initialize the database
    init_db()
    # Run the app
    app.run(host='0.0.0.0', port=5000)
