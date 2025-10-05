from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # change this to a random secure key


# ---------- Database Initialization ----------
def init_db():
    conn = sqlite3.connect('expenses.db')
    cur = conn.cursor()
    
    # Users table
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL)''')

    # Categories table
    cur.execute('''CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL)''')

    # Expenses table
    cur.execute('''CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    category_id INTEGER,
                    amount REAL,
                    description TEXT,
                    date TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(category_id) REFERENCES categories(id))''')
    # Insert default categories if none exist
    cur.execute('SELECT COUNT(*) FROM categories')
    if cur.fetchone()[0] == 0:
        default_categories = ['Food', 'Travel', 'Bills', 'Shopping', 'Other']
        cur.executemany('INSERT INTO categories (name) VALUES (?)',
                            [(cat,) for cat in default_categories])
    
    conn.commit()
    conn.close()


# ---------- Helper Functions ----------
def get_db_connection():
    conn = sqlite3.connect('expenses.db')
    conn.row_factory = sqlite3.Row
    return conn


# ---------- Routes ----------
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.')
        finally:
            conn.close()
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/index')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    expenses = conn.execute('''SELECT e.id, e.amount, e.description, e.date, c.name AS category
                               FROM expenses e
                               LEFT JOIN categories c ON e.category_id = c.id
                               WHERE e.user_id=?''', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('index.html', expenses=expenses)


@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    if request.method == 'POST':
        amount = request.form['amount']
        category_id = request.form['category']
        description = request.form['description']
        date = request.form['date']
        conn.execute('INSERT INTO expenses (user_id, category_id, amount, description, date) VALUES (?, ?, ?, ?, ?)',
                     (session['user_id'], category_id, amount, description, date))
        conn.commit()
        conn.close()
        flash('Expense added successfully!')
        return redirect(url_for('index'))
    conn.close()
    return render_template('add_expense.html', categories=categories)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_expense(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    expense = conn.execute('SELECT * FROM expenses WHERE id=?', (id,)).fetchone()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    if request.method == 'POST':
        amount = request.form['amount']
        category_id = request.form['category']
        description = request.form['description']
        date = request.form['date']
        conn.execute('UPDATE expenses SET amount=?, category_id=?, description=?, date=? WHERE id=?',
                     (amount, category_id, description, date, id))
        conn.commit()
        conn.close()
        flash('Expense updated successfully!')
        return redirect(url_for('index'))
    conn.close()
    return render_template('update_expense.html', expense=expense, categories=categories)


@app.route('/delete/<int:id>')
def delete_expense(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM expenses WHERE id=?', (id,))
    conn.commit()
    conn.close()
    flash('Expense deleted successfully!')
    return redirect(url_for('index'))


@app.route('/categories', methods=['GET', 'POST'])
def categories():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        try:
            conn.execute('INSERT INTO categories (name) VALUES (?)', (name,))
            conn.commit()
            flash('Category added!')
        except sqlite3.IntegrityError:
            flash('Category already exists!')
    categories = conn.execute('SELECT * FROM categories').fetchall()
    conn.close()
    return render_template('categories.html', categories=categories)


@app.route('/summary')
def summary():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    summary_data = conn.execute('''SELECT c.name AS category, SUM(e.amount) AS total
                                   FROM expenses e
                                   LEFT JOIN categories c ON e.category_id = c.id
                                   WHERE e.user_id=?
                                   GROUP BY c.name''', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('summary.html', summary=summary_data)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
