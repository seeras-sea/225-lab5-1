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
            .btn { 
                padding: 8px 15px; 
                color: white; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer;
                transition: background-color 0.3s;
                text-decoration: none;
                display: inline-block;
                margin-right: 5px;
            }
            .delete-btn { 
                background-color: #e74c3c; 
            }
            .delete-btn:hover { 
                background-color: #c0392b; 
            }
            .edit-btn {
                background-color: #f39c12;
            }
            .edit-btn:hover {
                background-color: #d35400;
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
            .modal {
                display: none;
                position: fixed;
                z-index: 1;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                overflow: auto;
                background-color: rgba(0,0,0,0.4);
            }
            .modal-content {
                background-color: #fefefe;
                margin: 15% auto;
                padding: 20px;
                border: 1px solid #888;
                width: 80%;
                max-width: 500px;
                border-radius: 8px;
            }
            .close {
                color: #aaa;
                float: right;
                font-size: 28px;
                font-weight: bold;
                cursor: pointer;
            }
            .close:hover {
                color: black;
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
                    <th>Actions</th>
                </tr>
                {% for contact in contacts %}
                <tr>
                    <td>{{ contact['id'] }}</td>
                    <td>{{ contact['name'] }}</td>
                    <td>{{ contact['phone'] }}</td>
                    <td>{{ contact['email'] }}</td>
                    <td>
                        <a href="#" onclick="openEditModal({{ contact['id'] }}, '{{ contact['name'] }}', '{{ contact['phone'] }}', '{{ contact['email'] }}')" class="btn edit-btn">Edit</a>
                        <form action="/delete/{{ contact['id'] }}" method="post" style="display: inline;">
                            <button type="submit" class="btn delete-btn">Delete</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </table>
            {% else %}
            <div class="empty-message">No contacts found. Add your first contact above!</div>
            {% endif %}
        </div>
        
        <!-- Edit Modal -->
        <div id="editModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeEditModal()">&times;</span>
                <h3>Edit Contact</h3>
                <form id="editForm" action="/edit" method="post">
                    <input type="hidden" id="editId" name="id">
                    <input type="text" id="editName" name="name" placeholder="Name" required>
                    <input type="text" id="editPhone" name="phone" placeholder="Phone" required>
                    <input type="email" id="editEmail" name="email" placeholder="Email" required>
                    <input type="submit" value="Save Changes">
                </form>
            </div>
        </div>
        
        <script>
            // Get the modal
            var modal = document.getElementById("editModal");
            
            // Function to open the edit modal
            function openEditModal(id, name, phone, email) {
                document.getElementById("editId").value = id;
                document.getElementById("editName").value = name;
                document.getElementById("editPhone").value = phone;
                document.getElementById("editEmail").value = email;
                modal.style.display = "block";
            }
            
            // Function to close the edit modal
            function closeEditModal() {
                modal.style.display = "none";
            }
            
            // Close the modal when clicking outside of it
            window.onclick = function(event) {
                if (event.target == modal) {
                    closeEditModal();
                }
            }
        </script>
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

@app.route('/edit', methods=['POST'])
def edit_contact():
    id = request.form['id']
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    
    db = get_db()
    db.execute('UPDATE contacts SET name = ?, phone = ?, email = ? WHERE id = ?', 
               (name, phone, email, id))
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
