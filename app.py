from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import mysql.connector
from mysql.connector import Error
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os 
from models import db, Feed

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
jwt = JWTManager(app)

PLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4'}

# ✅ MySQL Configuration (change if needed)
db_config = {
    'host': 'localhost',
    'user': 'root',           # Your MySQL username
    'password': 'Root@12345', # Your MySQL password
    'database': 'crowdcount_db'
}
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Root%4012345@localhost/crowdcount_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
with app.app_context():
    db.reflect()
Feed = db.Model.metadata.tables['feeds']    
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# ---------- Database Connection ----------
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Database error: {e}")
        return None

# ---------- HOME ----------
@app.route('/')
def home():
    return redirect(url_for('login'))

# ---------- REGISTER ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        role = request.form.get('role')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, first_name, last_name, email, role, password)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (username, first_name, last_name, email, role, password))
        conn.commit()
        conn.close()
        flash("Registered successfully! Please log in.")
        return redirect(url_for('login'))

    return render_template('register.html')

# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    username = data.get('username')
    password = data.get('password')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = user['username']
            session['role'] = user['role']
            flash(f"Welcome back, {user['username']}!")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password")
        if not user:
            return jsonify({"msg": "Invalid username or password"}), 401
        access_token = create_access_token(identify={'id': user[id], 'username': user[username], 'role': user[role] })
        return jsonify(access_token=access_token)

    return render_template('login.html')

# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM feeds")
    total_feeds = cursor.fetchone()[0]

    conn.close()

    return render_template('dashboard.html',
                           username=session['username'],
                           total_users=total_users,
                           total_feeds=total_feeds)

# ---------- USERS PAGE ----------
@app.route('/users')
def users():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users_list = cursor.fetchall()
    conn.close()

    return render_template('users.html', users=users_list)

# ---------- ADD USER ----------
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form.get('username')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        role = request.form.get('role')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, first_name, last_name, email, role, password)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (username, first_name, last_name, email, role, password))
        conn.commit()
        conn.close()

        flash("User added successfully!")
        return redirect(url_for('users'))

    return render_template('add_user.html')

# ---------- EDIT USER ----------
@app.route('/edit_user/<id>', methods=['GET', 'POST'])
def edit_user(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch user details
    cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
    user = cursor.fetchone()

    if not user:
        flash("User not found!", "danger")
        conn.close()
        return redirect(url_for('users'))

    # Handle form submission
    if request.method == 'POST':
        username = request.form['username']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        role = request.form['role']

        cursor.execute("""
            UPDATE users
            SET username = %s,
                first_name = %s,
                last_name = %s,
                email = %s,
                role = %s
            WHERE id = %s
        """, (username, first_name, last_name, email, role, id))
        
        conn.commit()
        conn.close()
        flash("User details updated successfully!", "success")
        return redirect(url_for('users'))

    conn.close()
    return render_template('edit_user.html', user=user)

# ---------- DELETE USER ----------
@app.route('/delete_user/<int:id>')
def delete_user(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    flash("User deleted successfully!")
    return redirect(url_for('users'))

# ---------- FEEDS PAGE ----------
@app.route('/feeds')
def feeds():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM feeds")
    feeds_list = cursor.fetchall()
    conn.close()
    
    return render_template('feeds.html', feeds=feeds_list)
# ---------- ADD FEED ----------
@app.route('/add_feed', methods=['GET', 'POST'])
def add_feed():
    if request.method == 'POST':
        feed_name = request.form.get('feed_name')
        feed_type = request.form.get('feed_type')
        assigned_user = request.form.get('Assigned user')
        video_filename = request.files.get('video_filename')

        # Optional: save uploaded file
        filename = None
        if video_filename and video_filename.filename != '':
            upload_folder = os.path.join('static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            filename = secure_filename(video_filename.filename)
            video_filename.save(os.path.join(upload_folder, filename))
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO feeds(name, type, video_filename, assigned_user)
            VALUES(%s, %s, %s, %s)
        """,  (feed_name, feed_type, video_filename, assigned_user))
        conn.commit()
        conn.close()

        flash("Feed added successfully!")
        return redirect('/feeds')

    # For GET request → just show form
    return render_template('add_feed.html')
# ---------- EDIT FEED ----------
@app.route('/edit_feed/<id>', methods=['GET', 'POST'])
def edit_feed(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT username FROM users")
    users = cursor.fetchall()

    cursor.execute("SELECT * FROM feeds WHERE id=%s", (id,))
    feed = cursor.fetchone()

    if request.method == 'POST':
        name = request.form.get('name')
        type_ = request.form.get('type')
        assigned_user = request.form.get('assigned_user')

        # Handle file upload
        file = request.files.get('video_filename')
        if file and file.filename != '':
            from werkzeug.utils import secure_filename
            filename = secure_filename(file.filename)
            upload_folder = os.path.join('static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file.save(os.path.join(upload_folder, filename))
        else:
            filename = feed['video_filename']  # Keep old file

        cursor.execute("""
            UPDATE feeds
            SET name=%s, type=%s, video_filename=%s, assigned_user=%s
            WHERE id=%s
        """, (name, type_, filename, assigned_user, id))

        conn.commit()
        conn.close()
        flash("Feed updated successfully!")
        return redirect(url_for('feeds'))

    conn.close()
    return render_template('edit_feed.html', feed=feed, users=users)

# ---------- DELETE FEED ----------
@app.route('/delete_feed/<id>')
def delete_feed(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM feeds WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    flash("Feed deleted successfully!")
    return redirect(url_for('feeds'))

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!")
    return redirect(url_for('login'))

# ---------- Run Server ----------
if __name__ == '_main_':
    app.run(debug=True)