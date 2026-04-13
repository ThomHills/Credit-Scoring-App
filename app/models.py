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