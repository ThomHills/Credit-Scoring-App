from app.db import db

# -----------------------
# USER MODEL
# -----------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


# -----------------------
# APPLICATION MODEL
# -----------------------
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # German Credit dataset features
    duration = db.Column(db.Float)
    amount = db.Column(db.Float)
    installment_rate = db.Column(db.Float)
    age = db.Column(db.Float)
    existing_credits = db.Column(db.Float)

    # Model outputs
    score = db.Column(db.Float)
    risk = db.Column(db.String(10))
    decision = db.Column(db.String(10))