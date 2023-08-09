from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os


app = Flask(__name__)
app.secret_key = 'secret_key'  # Change this to a secure secret key

# Create the uploads directory if it doesn't exist
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# User Authentication and Authorization

def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if 'user_id' in session:
            return route_function(*args, **kwargs)
        else:
            return redirect(url_for('login'))

    return wrapper


@app.route('/')
def index():
    if 'user_id' in session:
        user_id = session['user_id']
        conn = sqlite3.connect('items.db')
        conn.execute('CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT, description TEXT, user_id INTEGER, filename TEXT)')

        cursor = conn.execute('SELECT * FROM items WHERE user_id = ?', (user_id,))
        items = cursor.fetchall()
        return render_template('index.html', items=items)
    return redirect(url_for('login'))


@app.route('/delete/<int:item_id>', methods=['POST'])
@login_required
def delete(item_id):
    user_id = session['user_id']
    conn = sqlite3.connect('items.db')
    conn.execute('DELETE FROM items WHERE id = ? AND user_id = ?', (item_id, user_id))
    conn.commit()

    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect('users.db')
        conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')

        cursor = conn.execute('SELECT id, password FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user is not None and check_password_hash(user[1], password):
            print('login successful')
            session['user_id'] = user[0]
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


# Search and Filtering

@app.route('/search', methods=['POST'])
@login_required
def search():
    search_query = request.form['search_query']
    user_id = session['user_id']

    conn = sqlite3.connect('items.db')
    cursor = conn.execute(
        'SELECT * FROM items WHERE user_id = ? AND (name LIKE ? OR description LIKE ?)',
        (user_id, f'%{search_query}%', f'%{search_query}%')
    )
    items = cursor.fetchall()

    return render_template('search_results.html', items=items)


# Pagination and Sorting

@app.route('/sort', methods=['POST'])
@login_required
def sort():
    sort_attribute = request.form['sort_attribute']
    user_id = session['user_id']

    conn = sqlite3.connect('items.db')
    cursor = conn.execute(
        f'SELECT * FROM items WHERE user_id = ? ORDER BY {sort_attribute}',
        (user_id,)
    )
    items = cursor.fetchall()

    return render_template('index.html', items=items)


# File Uploads

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        user_id = session['user_id']

        file = request.files['file']
        filename = file.filename
        #file.save(f'uploads/{filename}')
        file.save(os.path.join('uploads', filename))


        conn = sqlite3.connect('items.db')
        conn.execute('CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT, description TEXT, user_id INTEGER, filename TEXT)')
        conn.execute(
            'INSERT INTO items (name, description, user_id, filename) VALUES (?, ?, ?, ?)',
            (name, description, user_id, filename)
        )
        conn.commit()

        return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit(item_id):
    user_id = session['user_id']
    conn = sqlite3.connect('items.db')
    cursor = conn.execute('SELECT * FROM items WHERE id = ? AND user_id = ?', (item_id, user_id))
    item = cursor.fetchone()

    if item is None:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        file = request.files['file']
        if file.filename != '':
            filename = file.filename
            file.save(f'uploads/{filename}')
        else:
            filename = item[3]

        conn.execute(
            'UPDATE items SET name = ?, description = ?, filename = ? WHERE id = ?',
            (name, description, filename, item_id)
        )
        conn.commit()

        return redirect(url_for('index'))

    return render_template('edit.html', item=item)

app.run(host='0.0.0.0', port=8080)