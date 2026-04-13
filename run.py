from flask import Flask
from app.routes import main
from app.db import db
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = "supersecretkey"

    # --- DATABASE CONFIG ---
    db_url = os.environ.get("DATABASE_URL")

    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- INIT DB ---
    db.init_app(app)

    # --- IMPORT MODELS ---
    from app import models

    with app.app_context():
        db.create_all()

    # --- REGISTER ROUTES ---
    app.register_blueprint(main)

    return app

# 👇 THIS LINE IS CRITICAL FOR GUNICORN
app = create_app()