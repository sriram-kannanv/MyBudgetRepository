from flask import Flask, render_template, request, redirect, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="manager",
    database="my_budget"
)
cursor = db.cursor(dictionary=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_input = request.form['password']
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user['password'], password_input):
            session['user_id'] = user['id']
            return redirect('/dashboard')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category']
        reason = request.form['reason']
        cursor.execute("INSERT INTO expenses (user_id, amount, category, reason) VALUES (%s, %s, %s, %s)",
                       (session['user_id'], amount, category, reason))
        db.commit()

    cursor.execute("SELECT * FROM expenses WHERE user_id = %s ORDER BY date DESC", (session['user_id'],))
    expenses = cursor.fetchall()
    return render_template('dashboard.html', expenses=expenses)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
