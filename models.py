# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ---------- USERS TABLE ----------
class User(db.Model):
    _tablename_ = 'users'  # must match your MySQL table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    role = db.Column(db.Enum('admin', 'user'), default='user')
    password = db.Column(db.String(255), nullable=False)


# ---------- FEEDS TABLE ----------
class Feed(db.Model):
    _tablename_ = 'feeds'  # must match MySQL table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.String(50))
    video_filename = db.Column(db.String(255))
    assigned_user = db.Column(db.String(50))