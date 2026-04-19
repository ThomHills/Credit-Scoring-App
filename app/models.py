from app.db import db

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    income = db.Column(db.Float)
    expenses = db.Column(db.Float)
    savings = db.Column(db.Float)
    missed = db.Column(db.Float)
    score = db.Column(db.Integer)
    risk = db.Column(db.String(20))
    decision = db.Column(db.String(20), default="Pending")

from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))  # 👈 ADD THIS