from flask import Flask, request, render_template_string, redirect
import sqlite3
import os

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
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; 
                padding: 0; 
                background-color: #f0f2f5; 
                color: #333;
            }
            h1 { 
                color: #2c3e50; 
                text-align: center;
                margin-bottom: 30px;
            }
            h3 {
                color: #3498db;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                margin-top: 30px;
            }
            .container { 
                max-width: 900px; 
                margin: 40px auto; 
                background-color: white; 
                padding: 30px; 
                border-radius: 8px; 
                box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
            }
            table { 
                width: 100%; 
                border-collapse: collapse; 
                margin-top: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }
            th, td { 
                padding: 15px; 
                text-align: left; 
                border-bottom: 1px solid #e1e1e1; 
            }
            th { 
                background-color: #3498db; 
                color: white;
                font-weight: 500;
            }
            tr:hover {
                background-color: #f5f7fa;
            }
            form { 
                margin-top: 20px; 
                background-color: #f9f9f9;
                padding: 20px;
                border-radius: 5px;
            }
            input[type="text"], input[type="email"] { 
                padding: 12px; 
                width: 100%; 
                margin-bottom: 15px; 
                border: 1px solid #ddd; 
                border-radius: 4px;
                font-size: 16px;
                transition: border 0.3s;
            }
            input[type="text"]:focus, input[type="email"]:focus {
                border-color: #3498db;
                outline: none;
                box-shadow: 0 0 5px rgba(52, 152, 219, 0.5);
            }
            input[type="submit"] { 
                padding: 12px 20px; 
                background-color: #3498db; 
                color: white; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer;
                font-size: 16px;
                transition: background-color 0.3s;
            }
            input[type="submit"]:hover { 
                background-color: #2980b9; 
            }
            .delete-btn { 
                padding: 8px 15px; 
                background-color: #e74c3c; 
                color: white; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer;
                transition: background-color 0.3s;
            }
            .delete-btn:hover { 
                background-color: #c0392b; 
            }
            .empty-message {
                text-align: center;
                padding: 20px;
                color: #7f8c8d;
                font-style: italic;
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .header-title {
                margin: 0;
            }
            .count-badge {
                background-color: #3498db;
                color: white;
                padding: 5px 10px;
                border-radius: 20px;
                font-size: 14px;
            }
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
            
            <div class="header">
                <h3 class="header-title">Contacts</h3>
                <span class="count-badge">{{ contacts|length }} contacts</span>
            </div>
            
            {% if contacts|length > 0 %}
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
            {% else %}
            <div class="empty-message">No contacts found. Add your first contact above!</div>
            {% endif %}
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
