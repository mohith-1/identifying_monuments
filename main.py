from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import mysql.connector

app = Flask(__name__)

# MySQL Configuration
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'monument_db'
}

# Session Configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'your_secret_key'
Session(app)

# Function to establish MySQL connection
def connect_to_mysql():
    try:
        conn = mysql.connector.connect(**mysql_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Route for homepage
@app.route('/')
def index():
    return redirect(url_for('login'))

# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = connect_to_mysql()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user:
                session['username'] = username
                return redirect(url_for('dashboard'))
            else:
                return "Invalid username or password"
        else:
            return "Unable to connect to database"
    return render_template('login.html')

# Route for registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = connect_to_mysql()
        if conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            cursor.close()
            conn.close()

            return render_template('login.html')
        else:
            return "Unable to connect to database"
    return render_template('register.html')

# Route for dashboard page
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    else:
        return redirect(url_for('login'))

# Logout 
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
